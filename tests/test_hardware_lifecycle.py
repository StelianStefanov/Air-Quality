"""Exercise real driver/framework lifecycle code with hardware I/O replaced."""

import importlib.util
import os
from pathlib import Path
import signal
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from src.lifecycle import close_resources, handle_sigterm


ROOT = Path(__file__).resolve().parents[1]


def module_with(name, **attributes):
    module = ModuleType(name)
    vars(module).update(attributes)
    return module


def load(test, name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    test.enterContext(patch.dict(sys.modules, {name: module}))
    spec.loader.exec_module(module)
    return module


class EnviroCleanupTests(unittest.TestCase):
    def setUp(self):
        self.logger = Mock()
        self.bus = Mock()
        self.bus_factory = Mock(return_value=self.bus)
        self.bme = Mock()
        self.bme_factory = Mock(return_value=self.bme)
        self.enterContext(patch.dict(sys.modules, {
            "smbus2": module_with("smbus2", SMBus=self.bus_factory),
            "bme280": module_with("bme280", BME280=self.bme_factory),
        }))
        self.module = load(self, "test_enviro_cleanup", ROOT / "src/sensors/enviro_sensor.py")

    def test_open_bus_is_retained_and_closed_once(self):
        sensor = self.module.EnviroSensor(self.logger)
        self.bus_factory.assert_called_once_with()
        self.bus.open.assert_called_once_with(1)
        self.bme_factory.assert_called_once_with(i2c_dev=self.bus)
        sensor.close()
        sensor.close()
        self.bus.close.assert_called_once()
        self.assertIsNone(sensor.enviro)
        self.assertIsNone(sensor.bus)

    def test_open_failure_after_resource_acquisition_closes_bus(self):
        self.bus.open.side_effect = OSError("ioctl failed after opening bus")
        sensor = self.module.EnviroSensor(self.logger)
        self.bus.close.assert_called_once()
        self.bme_factory.assert_not_called()
        self.assertIsNone(sensor.enviro)

    def test_bme_initialization_failure_closes_bus(self):
        self.bme_factory.side_effect = RuntimeError("sensor unavailable")
        self.module.EnviroSensor(self.logger)
        self.bus.close.assert_called_once()

    def test_interrupt_during_initialization_closes_bus_and_propagates(self):
        self.bme_factory.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.module.EnviroSensor(self.logger)
        self.bus.close.assert_called_once()

    def test_failed_close_can_be_retried(self):
        self.bus.close.side_effect = [OSError("close failed"), None]
        sensor = self.module.EnviroSensor(self.logger)
        sensor.close()
        self.assertIs(sensor.bus, self.bus)
        sensor.close()
        self.assertIsNone(sensor.bus)
        self.assertEqual(self.bus.close.call_count, 2)

    def test_failed_sensor_keeps_zero_fallback(self):
        class MissingBME:
            def __init__(self, **kwargs):
                raise OSError("missing sensor")

        self.module.BME280 = MissingBME
        sensor = self.module.EnviroSensor(self.logger)
        self.assertEqual(sensor.get_data(), {"temperature": 0, "pressure": 0, "humidity": 0})


class PmsCleanupTests(unittest.TestCase):
    def setUp(self):
        # Load the pinned driver source, but replace GPIO, serial and sleeps.
        driver_path = importlib.util.find_spec("pms5003").origin
        self.logger = Mock()
        self.serial = Mock()
        self.serial_factory = Mock(return_value=self.serial)
        self.enable = Mock()
        self.reset = Mock()
        self.get_pin = Mock(side_effect=[(self.enable, 22), (self.reset, 27)])
        self.enterContext(patch.dict(sys.modules, {
            "serial": module_with("serial", Serial=self.serial_factory),
            "gpiod": module_with("gpiod", LineSettings=Mock()),
            "gpiod.line": module_with("gpiod.line",
                Direction=SimpleNamespace(OUTPUT=1), Value=SimpleNamespace(INACTIVE=0, ACTIVE=1)),
            "gpiodevice": module_with("gpiodevice", get_pin=self.get_pin),
        }))
        driver = load(self, "pms5003", driver_path)
        self.assertEqual(driver.__version__, "1.0.1")
        self.enterContext(patch.object(driver, "time", SimpleNamespace(sleep=Mock(), time=lambda: 0)))
        self.module = load(self, "test_pms_cleanup", ROOT / "src/sensors/pms_sensor.py")

    def test_close_releases_serial_and_both_gpio_requests_once(self):
        sensor = self.module.PmsSensor(self.logger)
        sensor.close()
        sensor.close()
        self.serial.close.assert_called_once()
        self.enable.release.assert_called_once()
        self.reset.release.assert_called_once()
        self.assertTrue(all(value == 0 for value in sensor.get_data().values()))

    def test_second_pin_failure_releases_first_pin(self):
        self.get_pin.side_effect = [(self.enable, 22), OSError("reset pin busy")]
        sensor = self.module.PmsSensor(self.logger)
        self.assertIsNone(sensor.pms)
        self.enable.release.assert_called_once()
        self.serial_factory.assert_not_called()

    def test_serial_open_failure_releases_gpio_requests(self):
        self.serial_factory.side_effect = OSError("serial unavailable")
        self.module.PmsSensor(self.logger)
        self.enable.release.assert_called_once()
        self.reset.release.assert_called_once()

    def test_reset_failure_after_serial_open_releases_everything(self):
        self.serial.flushInput.side_effect = OSError("reset failed")
        sensor = self.module.PmsSensor(self.logger)
        self.assertIsNone(sensor.pms)
        self.serial.close.assert_called_once()
        self.enable.release.assert_called_once()
        self.reset.release.assert_called_once()

    def test_interrupt_during_constructor_releases_everything(self):
        self.serial.flushInput.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.module.PmsSensor(self.logger)
        self.serial.close.assert_called_once()
        self.enable.release.assert_called_once()
        self.reset.release.assert_called_once()

    def test_serial_close_failure_does_not_skip_gpio_release(self):
        self.serial.close.side_effect = OSError("serial close failed")
        sensor = self.module.PmsSensor(self.logger)
        sensor.close()
        self.enable.release.assert_called_once()
        self.reset.release.assert_called_once()
        self.logger.exception.assert_called_once()

    def test_normal_reads_and_read_recovery_keep_resources_open(self):
        sensor = self.module.PmsSensor(self.logger)
        sensor.pms.read = Mock(side_effect=self.module.ReadTimeoutError("no frame"))
        self.assertTrue(all(value == 0 for value in sensor.get_data().values()))
        self.assertEqual(self.serial.flushInput.call_count, 2)  # Initial reset + recovery.
        self.serial.close.assert_not_called()
        self.enable.release.assert_not_called()
        self.reset.release.assert_not_called()
        sensor.close()

    def test_repeated_create_close_does_not_accumulate_file_descriptors(self):
        resources = []

        def resource(method):
            fd = os.open(os.devnull, os.O_RDWR)
            handle = Mock()
            getattr(handle, method).side_effect = lambda: os.close(fd)
            resources.append((handle, method))
            return handle

        self.serial_factory.side_effect = lambda *args, **kwargs: resource("close")
        self.get_pin.side_effect = lambda *args: (resource("release"), 0)
        for _ in range(50):
            sensor = self.module.PmsSensor(self.logger)
            sensor.close()
        self.assertEqual(len(resources), 150)
        for handle, method in resources:
            getattr(handle, method).assert_called_once()


def owner_modules(test):
    logger = Mock()
    enviro = Mock()
    enviro.get_data.return_value = {"temperature": 25, "pressure": 1000, "humidity": 40}
    pms = Mock()
    pms.get_data.return_value = {"smoke": 1, "metals": 2, "dust": 3, "mikro": 1, "small": 2, "medium": 3}
    gas = Mock()
    gas.get_data.return_value = {"oxide": 1, "reduce": 2, "nh3": 3}
    database = Mock()
    factories = {"EnviroSensor": Mock(return_value=enviro), "PmsSensor": Mock(return_value=pms),
                 "EnviroGas": Mock(return_value=gas), "RedisDatabase": Mock(return_value=database)}
    utility = SimpleNamespace(logger=logger, temperature_compensation=lambda value: value,
                              get_ip_address=lambda: "127.0.0.1", get_overall_quality=lambda *args: " Good")
    test.enterContext(patch.dict(sys.modules, {
        "src.sensors.enviro_sensor": module_with("src.sensors.enviro_sensor", EnviroSensor=factories["EnviroSensor"]),
        "src.sensors.pms_sensor": module_with("src.sensors.pms_sensor", PmsSensor=factories["PmsSensor"]),
        "src.sensors.enviro_gas": module_with("src.sensors.enviro_gas", EnviroGas=factories["EnviroGas"]),
        "src.redis_database": module_with("src.redis_database", RedisDatabase=factories["RedisDatabase"]),
        "src.utilities": module_with("src.utilities", Utilities=utility),
    }))
    test.enterContext(patch("src.logger.Logger", return_value=logger))
    display = load(test, "test_display_lifecycle", ROOT / "src/display.py")
    background = load(test, "test_background_lifecycle", ROOT / "background_data.py")
    return SimpleNamespace(logger=logger, enviro=enviro, pms=pms, gas=gas, database=database,
                           factories=factories, display=display, background=background)


class OwnerCleanupTests(unittest.TestCase):
    def setUp(self):
        self.fixture = owner_modules(self)

    def test_late_initialization_failure_closes_already_created_sensors(self):
        f = self.fixture
        error = ValueError("invalid Redis configuration")
        f.factories["RedisDatabase"].side_effect = error
        for constructor in (f.display.Display, f.background.BackgroundData):
            with self.subTest(owner=constructor.__name__):
                f.enviro.reset_mock()
                f.pms.reset_mock()
                with self.assertRaises(ValueError) as caught:
                    constructor(f.logger)
                self.assertIs(caught.exception, error)
                f.enviro.close.assert_called_once()
                f.pms.close.assert_called_once()
                f.gas.close.assert_not_called()

    def test_close_is_idempotent_and_does_not_close_shared_gas_module(self):
        f = self.fixture
        owner = f.background.BackgroundData(f.logger)
        owner.close()
        owner.close()
        owner._get_all_sensors_data()
        f.enviro.close.assert_called_once()
        f.pms.close.assert_called_once()
        f.database.db.close.assert_called_once()
        f.gas.close.assert_not_called()
        f.enviro.get_data.assert_not_called()

    def test_one_close_failure_does_not_skip_other_resources(self):
        f = self.fixture
        f.pms.close.side_effect = OSError("cannot close PMS")
        owner = f.background.BackgroundData(f.logger)
        owner.close()
        f.enviro.close.assert_called_once()
        f.database.db.close.assert_called_once()
        f.logger.exception.assert_called_once()

    def test_timer_stop_failure_does_not_skip_sensor_cleanup(self):
        f = self.fixture
        owner = f.display.Display(f.logger)
        owner._update_timer = Mock()
        owner._update_timer.stop.side_effect = RuntimeError("timer stop failed")
        owner.close()
        f.enviro.close.assert_called_once()
        f.pms.close.assert_called_once()
        f.database.db.close.assert_called_once()

    def test_background_entry_point_closes_on_interrupt_error_and_sigterm(self):
        f = self.fixture
        previous = signal.getsignal(signal.SIGTERM)
        def sigterm():
            signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)

        for failure in (KeyboardInterrupt(), RuntimeError("failed"), sigterm):
            with self.subTest(failure=failure):
                owner = Mock()
                owner._get_all_sensors_data.side_effect = failure
                with patch.object(f.background, "BackgroundData", return_value=owner):
                    if failure is sigterm:
                        with self.assertRaises(SystemExit) as caught:
                            f.background.main()
                        self.assertEqual(caught.exception.code, 143)
                    else:
                        f.background.main()
                owner.close.assert_called_once()
                self.assertEqual(signal.getsignal(signal.SIGTERM), previous)

    def test_display_entry_point_closes_on_return_interrupt_error_and_sigterm(self):
        f = self.fixture
        display_factory = Mock()
        with patch.dict(sys.modules, {"src.display": module_with("src.display", Display=display_factory)}):
            entry = load(self, "test_display_entry", ROOT / "main.py")
        def sigterm():
            signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)

        for failure in (None, KeyboardInterrupt(), RuntimeError("failed"), sigterm):
            with self.subTest(failure=failure):
                f.database.reset_mock()
                display = Mock()
                display.run.side_effect = failure
                display_factory.return_value = display
                if failure is sigterm:
                    with self.assertRaises(SystemExit):
                        entry.main()
                else:
                    entry.main()
                display.close.assert_called_once()
                f.database.db.close.assert_called_once()


class TextualShutdownTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_textual_unmount_releases_sensors_and_stops_polling(self):
        f = owner_modules(self)
        app = f.display.Display(f.logger)
        async with app.run_test():
            f.enviro.get_data.assert_called()
            f.enviro.close.assert_not_called()
            f.pms.close.assert_not_called()
        f.enviro.close.assert_called_once()
        f.pms.close.assert_called_once()
        f.database.db.close.assert_called_once()
        previous_reads = f.enviro.get_data.call_count
        app.close()
        app.update()
        self.assertEqual(f.enviro.get_data.call_count, previous_reads)
        f.enviro.close.assert_called_once()


class LifecycleHelperTests(unittest.TestCase):
    def test_sigterm_handler_restored_after_exception(self):
        previous = signal.getsignal(signal.SIGTERM)
        with self.assertRaises(RuntimeError):
            with handle_sigterm():
                raise RuntimeError("startup failed")
        self.assertEqual(signal.getsignal(signal.SIGTERM), previous)

    def test_cleanup_failure_preserves_original_exception(self):
        logger = Mock()
        first = Mock()
        first.close.side_effect = OSError("cleanup failed")
        second = Mock()
        original = RuntimeError("original failure")
        with self.assertRaises(RuntimeError) as caught:
            try:
                raise original
            finally:
                close_resources(logger, None, first, second)
        self.assertIs(caught.exception, original)
        second.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
