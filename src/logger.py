import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import RLock


_configuration_lock = RLock()


class Logger:
    """Configure one rotating file handler per service logger.

    Repeated setup reuses the handler; changing its destination or rotation
    settings closes and replaces it. Python's logging shutdown closes the
    remaining handlers when the process exits.
    """

    def __init__(
        self,
        logger_name: str,
        level: int,
        filename: str,
        *,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 3,
    ):
        if max_bytes <= 0 or backup_count < 1:
            raise ValueError("Log rotation requires max_bytes > 0 and backup_count >= 1")

        log_path = Path(filename).resolve()
        handler_name = f"{logger_name}.file"

        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        with _configuration_lock:
            self.log = logging.getLogger(logger_name)
            handlers = [h for h in self.log.handlers if h.get_name() == handler_name]
            self.file_handler = next(
                (
                    h
                    for h in handlers
                    if isinstance(h, RotatingFileHandler)
                    and h.baseFilename == str(log_path)
                    and h.maxBytes == max_bytes
                    and h.backupCount == backup_count
                    and h.stream is not None
                    and not h.stream.closed
                ),
                None,
            )

            if self.file_handler is None:
                log_path.parent.mkdir(parents=True, exist_ok=True)
                # Open the replacement first so failed setup preserves the old log.
                self.file_handler = RotatingFileHandler(
                    log_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8",
                )

            for handler in handlers:
                if handler is not self.file_handler:
                    self.log.removeHandler(handler)
                    handler.close()

            self.file_handler.set_name(handler_name)
            self.file_handler.setFormatter(formatter)
            self.log.addHandler(self.file_handler)
            self.log.setLevel(level)
            self.log.propagate = False

    def error(self, message):
        self.log.error(message)

    def info(self, message):
        self.log.info(message)

    def warning(self, message):
        self.log.warning(message)

    def debug(self, message):
        self.log.debug(message)

    def critical(self, message):
        self.log.critical(message)

    def exception(self, message):
        self.log.exception(message)
