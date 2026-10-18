"""Startup module"""

import logging

from src.display import Display
from src.logger import Logger
from src.main_config import main_cnf
from src.utilities import Utilities
from src.redis_database import RedisDatabase
from src.lifecycle import close_resources, handle_sigterm

main_logger = Logger(
    logger_name="Air.display",
    level=logging.INFO,
    filename=str(main_cnf.cli_log_path),
)

Utilities.logger = main_logger


def main():
    with handle_sigterm():
        redis_db = None
        display = None
        try:
            redis_db = RedisDatabase(main_logger)
            redis_db.db.set("running_service", "display")
            display = Display(main_logger)
            display.run()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            main_logger.exception(e)
        finally:
            close_resources(main_logger, display, redis_db.db if redis_db is not None else None)


if __name__ == "__main__":
    main()
