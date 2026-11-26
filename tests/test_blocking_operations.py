"""Run with unittest after installing requirements-test.txt; no live services needed."""

import asyncio
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
import redis
import uvicorn
from uvicorn.protocols.http.h11_impl import H11Protocol
from uvicorn.server import ServerState

from src.main_config import main_cnf
from src.redis_database import RedisDatabase, SensorDataUnavailable


ROOT = Path(__file__).resolve().parents[1]
LIMITS = {
    "CPU_TEMPERATURE_TIMEOUT": "1",
    "REDIS_CONNECT_TIMEOUT": "1",
    "REDIS_SOCKET_TIMEOUT": "1",
    "REDIS_MAX_CONNECTIONS": "32",
}
SENSOR_DATA = {
    "temperature": 25, "pressure": 1000, "humidity": 40,
    "smoke": 1, "metals": 2, "dust": 3,
    "oxide": 1, "reduce": 2, "nh3": 3,
    "mikro": 1, "small": 2, "medium": 3, "quality": " Good",
}


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_utilities():
    netifaces = ModuleType("netifaces")
    netifaces.interfaces = lambda: []
    netifaces.ifaddresses = lambda _: {}
    netifaces.AF_INET = 2
    with patch.dict(sys.modules, {"netifaces": netifaces}):
        module = load_module("test_operation_utilities", "src/utilities.py")
    module.Utilities.logger = Mock()
    return module


class LimitConfigurationTests(unittest.TestCase):
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(main_cnf.cpu_temperature_timeout, 1)
            self.assertEqual(main_cnf.redis_connect_timeout, 1)
            self.assertEqual(main_cnf.redis_socket_timeout, 1)
            self.assertEqual(main_cnf.redis_max_connections, 32)

    def test_timeout_overrides_and_invalid_values(self):
        settings = {
            "CPU_TEMPERATURE_TIMEOUT": "cpu_temperature_timeout",
            "REDIS_CONNECT_TIMEOUT": "redis_connect_timeout",
            "REDIS_SOCKET_TIMEOUT": "redis_socket_timeout",
        }
        for name, attribute in settings.items():
            with patch.dict(os.environ, {name: "0.25"}):
                self.assertEqual(getattr(main_cnf, attribute), 0.25)
            for value in ("0", "-1", "nan", "inf", "", "invalid"):
                with self.subTest(name=name, value=value):
                    with patch.dict(os.environ, {name: value}):
                        with self.assertRaisesRegex(ValueError, name):
                            getattr(main_cnf, attribute)

    def test_connection_limit_requires_positive_integer(self):
        with patch.dict(os.environ, {"REDIS_MAX_CONNECTIONS": "4"}):
            self.assertEqual(main_cnf.redis_max_connections, 4)
        for value in ("0", "-1", "1.5", "inf", "", "invalid"):
            with self.subTest(value=value):
                with patch.dict(os.environ, {"REDIS_MAX_CONNECTIONS": value}):
                    with self.assertRaises(ValueError):
                        main_cnf.redis_max_connections


class TemperatureTests(unittest.TestCase):
    def setUp(self):
        self.module = load_utilities()
        self.enterContext(patch.dict(os.environ, LIMITS))

    def test_one_timed_command_per_calculation(self):
        result = SimpleNamespace(stdout="temp=50.0'C\n")
        with patch.object(self.module, "run", return_value=result) as run:
            self.assertEqual(self.module.Utilities.temperature_compensation(30), 20)
        run.assert_called_once_with(
            ["vcgencmd", "measure_temp"], capture_output=True, text=True,
            check=True, timeout=1.0,
        )

    def test_command_failures_return_raw_temperature(self):
        for error in (
            subprocess.TimeoutExpired("vcgencmd", 1),
            subprocess.CalledProcessError(1, "vcgencmd"),
            FileNotFoundError("vcgencmd unavailable"),
            PermissionError("cannot execute vcgencmd"),
        ):
            with self.subTest(error=type(error).__name__):
                with patch.object(self.module, "run", side_effect=error):
                    self.assertEqual(self.module.Utilities.temperature_compensation(25), 25)
                self.module.Utilities.logger.exception.assert_called_with(error)

    def test_malformed_output_returns_raw_temperature(self):
        for output in ("", "50", "temp=nan'C", "temp=inf'C", "error", "temp=50'F"):
            with self.subTest(output=output):
                with patch.object(self.module, "run", return_value=SimpleNamespace(stdout=output)):
                    self.assertEqual(self.module.Utilities.temperature_compensation(25), 25)

    def test_timeout_kills_and_reaps_real_child_and_closes_pipes(self):
        processes = []
        original_popen = subprocess.Popen
        original_run = subprocess.run

        def track_process(*args, **kwargs):
            process = original_popen(*args, **kwargs)
            processes.append(process)
            return process

        def run_sleeping_child(command, **kwargs):
            return original_run([sys.executable, "-c", "import time; time.sleep(30)"], **kwargs)

        with patch.dict(os.environ, {"CPU_TEMPERATURE_TIMEOUT": "0.1"}):
            with patch.object(self.module, "run", side_effect=run_sleeping_child):
                with patch("subprocess.Popen", side_effect=track_process):
                    self.assertEqual(self.module.Utilities.temperature_compensation(25), 25)
        self.assertEqual(len(processes), 1)
        process = processes[0]
        self.assertIsNotNone(process.returncode)
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)


class RedisTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, LIMITS))
        self.logger = Mock()
        self.database = RedisDatabase(self.logger)
        self.addCleanup(self.database.db.close)

    def test_connection_settings_and_zero_retries(self):
        pool = self.database.db.connection_pool
        self.assertEqual(pool.max_connections, 32)
        self.assertEqual(pool.connection_kwargs["socket_connect_timeout"], 1)
        self.assertEqual(pool.connection_kwargs["socket_timeout"], 1)
        operation = Mock(side_effect=redis.TimeoutError("stalled"))
        with self.assertRaises(redis.TimeoutError):
            pool.connection_kwargs["retry"].call_with_retry(operation, Mock())
        operation.assert_called_once()

    def test_connect_timeout_is_not_retried_and_pool_recovers(self):
        pool = self.database.db.connection_pool
        with patch.object(pool.connection_class, "_connect", side_effect=socket.timeout) as connect:
            with self.assertRaises(SensorDataUnavailable):
                self.database.get_running_service()
        connect.assert_called_once()
        self.assertEqual(len(pool._in_use_connections), 0)
        with patch.object(self.database.db, "get", return_value="background"):
            self.assertEqual(self.database.get_running_service(), "background")

    def test_pool_exhaustion_fails_promptly_and_released_connection_is_reusable(self):
        pool = self.database.db.connection_pool
        pool.max_connections = 1
        with patch.object(pool.connection_class, "connect"):
            with patch.object(pool.connection_class, "can_read", return_value=False):
                connection = pool.get_connection()
                try:
                    with self.assertRaises(SensorDataUnavailable):
                        self.database.get_sensor_data("sensor_data_background")
                finally:
                    pool.release(connection)
                reused = pool.get_connection()
                self.assertIs(reused, connection)
                pool.release(reused)

    def test_read_failures_are_explicit_and_recovery_returns_data(self):
        for error in (redis.TimeoutError("stalled"), redis.ConnectionError("offline")):
            with self.subTest(error=type(error).__name__):
                with patch.object(self.database.db, "get", side_effect=error):
                    with self.assertRaises(SensorDataUnavailable):
                        self.database.get_sensor_data("sensor_data_background")
        with patch.object(self.database.db, "get", return_value=json.dumps(SENSOR_DATA)):
            self.assertEqual(self.database.get_sensor_data("sensor_data_background"), SENSOR_DATA)

    def test_missing_or_invalid_data_is_unavailable(self):
        for value in (None, "invalid json", "null", "[]", "{}"):
            with self.subTest(value=value):
                with patch.object(self.database.db, "get", return_value=value):
                    with self.assertRaises(SensorDataUnavailable):
                        self.database.get_sensor_data("sensor_data_background")

    def test_failed_write_logs_and_allows_next_cycle(self):
        error = redis.TimeoutError("stalled")
        with patch.object(self.database.db, "set", side_effect=[error, True]) as write:
            self.database.save_sensor_data("sensor_data_background", SENSOR_DATA)
            self.database.save_sensor_data("sensor_data_background", SENSOR_DATA)
        self.assertEqual(write.call_count, 2)
        self.logger.exception.assert_called_once_with(error)


class WebRequestTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, LIMITS))
        utilities = load_utilities()
        with patch.dict(sys.modules, {"src.utilities": utilities}):
            with patch("src.logger.Logger", return_value=Mock()):
                self.server = load_module("test_operation_server", "src/web/server.py")
        self.addCleanup(self.server.redis_db.db.close)
        self.get = self.enterContext(patch.object(self.server.redis_db.db, "get"))
        self.temperature = self.enterContext(patch.object(
            self.server.Utilities, "temperature_compensation", return_value=22,
        ))
        self.weather = self.enterContext(patch.object(self.server, "CurrentWeather"))
        self.weather.return_value.return_weather_data.return_value = {"temp": 10, "weather": "Clear"}
        self.client = self.enterContext(TestClient(self.server.app))

    def test_redis_lookup_and_sensor_read_timeouts_return_503(self):
        for path in ("/", "/air", "/dev", "/api/air-data"):
            for phase in ("service", "data"):
                with self.subTest(path=path, phase=phase):
                    error = redis.TimeoutError("internal connection details")
                    self.get.side_effect = error if phase == "service" else ["background", error]
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.json(), {"detail": "Sensor data is temporarily unavailable"})
                    self.assertEqual(response.headers["retry-after"], "2")
        self.temperature.assert_not_called()
        self.weather.assert_not_called()

    def test_missing_data_returns_503(self):
        self.get.side_effect = [None, None]
        self.assertEqual(self.client.get("/api/air-data").status_code, 503)

    def test_next_request_recovers_after_redis_failure(self):
        self.get.side_effect = [redis.ConnectionError("offline"), "background", json.dumps(SENSOR_DATA)]
        self.assertEqual(self.client.get("/api/air-data").status_code, 503)
        response = self.client.get("/api/air-data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["temp"], "22°C")

    def test_clock_has_no_external_dependency_calls(self):
        self.get.side_effect = AssertionError("Clock must not read Redis")
        self.temperature.side_effect = AssertionError("Clock must not run vcgencmd")
        self.weather.side_effect = AssertionError("Clock must not fetch weather")
        response = self.client.get("/clock")
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="main_clock"', response.text)
        self.assertIn("?v=1.01", response.text)
        self.get.assert_not_called()
        self.temperature.assert_not_called()
        self.weather.assert_not_called()


class ConcurrencyLimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_uvicorn_rejects_overload_and_accepts_requests_after_recovery(self):
        started = asyncio.Event()
        release = asyncio.Event()
        calls = []

        async def slow_app(scope, receive, send):
            calls.append(scope["path"])
            started.set()
            await release.wait()
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        config = uvicorn.Config(slow_app, limit_concurrency=2, lifespan="off", log_config=None)
        state = ServerState()
        protocols = []

        def request():
            transport = Mock()
            transport.get_extra_info.return_value = None
            transport.is_closing.return_value = False
            protocol = H11Protocol(config, server_state=state, app_state={})
            protocols.append(protocol)
            protocol.connection_made(transport)
            protocol.data_received(b"GET / HTTP/1.1\r\nHost: test\r\nConnection: close\r\n\r\n")
            return protocol, transport

        try:
            first, _ = request()
            await asyncio.wait_for(started.wait(), timeout=2)
            previous_tasks = set(state.tasks)
            second, transport = request()
            await asyncio.wait_for(asyncio.gather(*(state.tasks - previous_tasks)), timeout=2)
            output = b"".join(call.args[0] for call in transport.write.call_args_list)
            self.assertIn(b"503 Service Unavailable", output)
            self.assertEqual(len(calls), 1)
            second.connection_lost(None)

            release.set()
            await asyncio.wait_for(asyncio.gather(*state.tasks), timeout=2)
            first.connection_lost(None)
            _, recovered_transport = request()
            await asyncio.wait_for(asyncio.gather(*state.tasks), timeout=2)
            output = b"".join(call.args[0] for call in recovered_transport.write.call_args_list)
            self.assertIn(b"200 OK", output)
            self.assertEqual(len(calls), 2)
        finally:
            release.set()
            await asyncio.gather(*state.tasks, return_exceptions=True)
            for protocol in protocols:
                protocol.connection_lost(None)


if __name__ == "__main__":
    unittest.main()
