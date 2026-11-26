from pathlib import Path
import math
import os

from dotenv import load_dotenv


class MainConfig:
    def __init__(self):
        load_dotenv()

    @property
    def get_screen_title(self) -> str:
        return os.getenv("TITLE_SCREEN", default="Air Quality")

    @property
    def root_dir(self) -> Path:
        """Project root"""

        return Path.cwd()

    @property
    def assets_version(self) -> float:
        return os.getenv("ASSETS_VERSION", default=1.01)

    @property
    def compensation_temp_factor(self) -> float:
        """There is a temperature compensation, because of the raspberry and the sensor are heating up at the same time"""

        compensation_factor = os.getenv("COMPENSATION_TEMP_FACTOR")
        default_factor = 4.35

        if not compensation_factor:
            return default_factor

        try:
            return float(compensation_factor)
        except ValueError:
            return default_factor

    @property
    def web_interval_reload(self) -> int:
        return int(os.getenv("WEB_INTERVAL_RELOAD", default=2))

    @staticmethod
    def _positive_float(name: str, default: float) -> float:
        try:
            value = float(os.getenv(name, default))
        except ValueError as error:
            raise ValueError(f"{name} must be a finite positive number") from error
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive number")
        return value

    @property
    def cpu_temperature_timeout(self) -> float:
        return self._positive_float("CPU_TEMPERATURE_TIMEOUT", 1.0)

    @property
    def redis_connect_timeout(self) -> float:
        return self._positive_float("REDIS_CONNECT_TIMEOUT", 1.0)

    @property
    def redis_socket_timeout(self) -> float:
        return self._positive_float("REDIS_SOCKET_TIMEOUT", 1.0)

    @property
    def redis_max_connections(self) -> int:
        try:
            value = int(os.getenv("REDIS_MAX_CONNECTIONS", "32"))
        except ValueError as error:
            raise ValueError("REDIS_MAX_CONNECTIONS must be a positive integer") from error
        if value <= 0:
            raise ValueError("REDIS_MAX_CONNECTIONS must be a positive integer")
        return value

    @property
    def cli_log_path(self) -> Path:
        return self.root_dir / "logs" / "cli.log"

    @property
    def background_log_path(self) -> Path:
        return self.root_dir / "logs" / "background.log"

    @property
    def web_log_path(self) -> Path:
        return self.root_dir / "logs" / "web.log"


main_cnf = MainConfig()
