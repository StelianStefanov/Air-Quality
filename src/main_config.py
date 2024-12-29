from pathlib import Path
import os

from dotenv import load_dotenv


class MainConfig:
    def __init__(self):
        load_dotenv()

    @property
    def get_net_interfaces(self) -> list[str]:
        dotenv_intrfaces = os.getenv("NET_INTERFACES")

        if not dotenv_intrfaces:
            return ["eth0", "wlan0", "enp60s0"]

        return os.getenv("NET_INTERFACES").split(",")

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
        compensation_factor = os.getenv("COMPENSATION_TEMP_FACTOR")
        default_factor = 4.35

        if not compensation_factor:
            return default_factor

        try:
            return float(compensation_factor)
        except ValueError:
            return default_factor


main_cnf = MainConfig()
