import logging


class Logger:
    def __init__(self, logger_name: str, level: int, filename: str):
        self.log = logging.getLogger(logger_name)
        self.log.setLevel(level)  # Set the logging level

        # Formatter for the logs
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # FileHandler to write logs to a file
        self.file_handler = logging.FileHandler(filename)
        self.file_handler.setFormatter(formatter)  # Attach the formatter to the handler
        self.log.addHandler(self.file_handler)

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
