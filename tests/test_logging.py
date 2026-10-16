"""Logging regression tests; no application services or hardware are started."""

from concurrent.futures import ThreadPoolExecutor
import gc
import importlib.util
import io
import logging
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import patch

from src.logger import Logger


class LoggingTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.loggers = set()
        self.addCleanup(self.close_handlers)

    def close_handlers(self):
        for logger in self.loggers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()

    def make_logger(self, service="default", path=None, level=logging.INFO, **options):
        name = f"AirLoggingTests.{self._testMethodName}.{service}"
        self.loggers.add(logging.getLogger(name))
        return Logger(name, level, str(path or self.directory / f"{service}.log"), **options)

    def test_repeated_setup_reuses_one_handler_and_file_descriptor(self):
        descriptors = Path("/proc/self/fd")
        before = len(list(descriptors.iterdir())) if descriptors.exists() else None
        first = self.make_logger()
        for _ in range(100):
            current = self.make_logger()
            self.assertIs(current.file_handler, first.file_handler)
        gc.collect()

        self.assertEqual(len(first.log.handlers), 1)
        if before is not None:
            self.assertEqual(len(list(descriptors.iterdir())), before + 1)
        first.info("one event")
        lines = (self.directory / "default.log").read_text().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("one event", lines[0])

    def test_concurrent_setup_reuses_one_handler(self):
        # Register the logger before starting threads to keep test bookkeeping local.
        first = self.make_logger()
        with ThreadPoolExecutor(max_workers=8) as executor:
            instances = list(executor.map(
                lambda _: Logger(first.log.name, logging.INFO, first.file_handler.baseFilename),
                range(100),
            ))
        self.assertEqual(len(first.log.handlers), 1)
        self.assertTrue(all(item.file_handler is first.file_handler for item in instances))

    def test_destination_change_closes_previous_file(self):
        first = self.make_logger()
        first.info("before change")
        old_stream = first.file_handler.stream
        replacement = self.make_logger(path=self.directory / "replacement.log")

        self.assertTrue(old_stream.closed)
        self.assertIsNone(first.file_handler.stream)
        self.assertEqual(first.log.handlers, [replacement.file_handler])
        # Existing wrappers also write through the newly configured named logger.
        first.info("after change")
        self.assertNotIn("after change", (self.directory / "default.log").read_text())
        self.assertIn("after change", (self.directory / "replacement.log").read_text())

    def test_rotation_configuration_change_closes_previous_file(self):
        first = self.make_logger()
        old_stream = first.file_handler.stream
        replacement = self.make_logger(max_bytes=512, backup_count=2)
        self.assertTrue(old_stream.closed)
        self.assertEqual(first.log.handlers, [replacement.file_handler])
        self.assertEqual(replacement.file_handler.maxBytes, 512)
        self.assertEqual(replacement.file_handler.backupCount, 2)

    def test_failed_reconfiguration_preserves_existing_handler(self):
        first = self.make_logger()
        with patch("src.logger.RotatingFileHandler._open", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                self.make_logger(path=self.directory / "unwritable.log")
        self.assertFalse(first.file_handler.stream.closed)
        self.assertEqual(first.log.handlers, [first.file_handler])
        first.info("still works")
        self.assertIn("still works", (self.directory / "default.log").read_text())

    def test_log_directory_is_created(self):
        path = self.directory / "nested" / "logs" / "service.log"
        self.make_logger(path=path).info("created")
        self.assertIn("created", path.read_text())

    def test_level_changes_without_reopening_file(self):
        first = self.make_logger()
        first.debug("hidden")
        second = self.make_logger(level=logging.DEBUG)
        second.debug("visible")
        self.assertIs(first.file_handler, second.file_handler)
        content = (self.directory / "default.log").read_text()
        self.assertNotIn("hidden", content)
        self.assertIn("visible", content)

    def test_records_do_not_propagate_to_parent_logger(self):
        parent = logging.getLogger("AirLoggingTests")
        self.loggers.add(parent)
        output = io.StringIO()
        parent.addHandler(logging.StreamHandler(output))
        self.make_logger().info("service event")
        self.assertEqual(output.getvalue(), "")
        self.assertEqual((self.directory / "default.log").read_text().count("service event"), 1)

    def test_services_write_to_separate_files(self):
        services = ("display", "background", "web")
        for service in services:
            self.make_logger(service).info(f"event from {service}")
        for service in services:
            content = (self.directory / f"{service}.log").read_text()
            self.assertIn(f"event from {service}", content)
            for other in services:
                if other != service:
                    self.assertNotIn(f"event from {other}", content)

    def test_rotation_limits_backups_and_retains_latest_records(self):
        logger = self.make_logger(max_bytes=512, backup_count=3)
        for number in range(100):
            logger.info(f"event-{number:03d} " + "x" * 80)

        files = sorted(self.directory.glob("default.log*"))
        self.assertEqual([path.name for path in files], [
            "default.log", "default.log.1", "default.log.2", "default.log.3",
        ])
        self.assertTrue(all(path.stat().st_size <= 512 for path in files))
        self.assertIn("event-099", (self.directory / "default.log").read_text())
        self.assertNotIn("event-000", "".join(path.read_text() for path in files))

    def test_exception_traceback_and_unicode_are_preserved(self):
        logger = self.make_logger()
        try:
            raise ValueError("sensor failure at 25°C")
        except ValueError as error:
            logger.exception(error)
        content = (self.directory / "default.log").read_text(encoding="utf-8")
        self.assertIn("Traceback (most recent call last)", content)
        self.assertIn("ValueError: sensor failure at 25°C", content)

    def load_utilities(self):
        # Only the network-interface dependency is stubbed; utility code is real.
        netifaces = ModuleType("netifaces")
        netifaces.interfaces = lambda: []
        netifaces.ifaddresses = lambda _: {}
        netifaces.AF_INET = 2
        path = Path(__file__).resolve().parents[1] / "src" / "utilities.py"
        spec = importlib.util.spec_from_file_location("logging_test_utilities", path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"netifaces": netifaces}):
            spec.loader.exec_module(module)
        return module

    def test_utilities_import_does_not_open_log_files(self):
        with patch("logging.FileHandler", side_effect=AssertionError("Unexpected file handler")):
            module = self.load_utilities()
        self.assertIsInstance(module.Utilities.logger, logging.Logger)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_utility_errors_use_injected_service_logger(self):
        module = self.load_utilities()
        module.Utilities.logger = self.make_logger("web")
        with patch.object(module, "Popen", side_effect=FileNotFoundError("vcgencmd unavailable")):
            self.assertEqual(module.Utilities.temperature_compensation(25), 25)
        content = (self.directory / "web.log").read_text()
        self.assertEqual(content.count("Traceback (most recent call last)"), 1)
        self.assertIn("vcgencmd unavailable", content)
        self.assertEqual([path.name for path in self.directory.iterdir()], ["web.log"])


if __name__ == "__main__":
    unittest.main()
