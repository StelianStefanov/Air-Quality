from pathlib import Path
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

    @property
    def cli_log_path(self) -> Path:
        return self.root_dir / "logs" / "cli.log"

    @property
    def web_log_path(self) -> Path:
        return self.root_dir / "logs" / "web.log"


main_cnf = MainConfig()
