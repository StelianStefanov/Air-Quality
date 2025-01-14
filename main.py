"""Startup module"""

import logging

from src.display import Display
from src.logger import Logger
from src.main_config import main_cnf
from src.utilities import Utilities

main_logger = Logger(
    logger_name="Air",
    level=logging.INFO,
    filename=str(main_cnf.cli_log_path),
)

Utilities.logger = main_logger


def main():
    try:
        Display(main_logger).run()
    except Exception as e:
        main_logger.exception(e)


if __name__ == "__main__":
    main()
