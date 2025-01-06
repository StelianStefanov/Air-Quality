import logging


class Logger:
    def __init__(self):
        self.log = logging.getLogger("custom_logger")  # Use a named logger to avoid conflicts
        self.log.setLevel(logging.INFO)  # Set the logging level

        # Formatter for the logs
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # FileHandler to write logs to a file
        self.file_handler = logging.FileHandler("log.log")
        self.file_handler.setFormatter(formatter)  # Attach the formatter to the handler
        self.log.addHandler(self.file_handler)

    def error(self, message):
        self.log.error(message)

    def info(self, message):
        self.log.info(message)

    def warning(self, message):
        self.log.warning(message)
