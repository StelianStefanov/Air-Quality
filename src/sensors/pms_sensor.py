from pms5003 import PMS5003
from src.logger import Logger


class PmsSensor:
    def __init__(self, main_logger: Logger):
        self.main_logger = main_logger
        self.pms = None

        try:
            self.pms = PMS5003(device="/dev/ttyAMA0", baudrate=9600)
        except Exception as e:
            self.main_logger.exception(e)

    def _get_pms(self) -> dict[str, int]:
        pms_data = {
            "smoke": 0,
            "metals": 0,
            "dust": 0,
            "mikro": 0,
            "small": 0,
            "medium": 0,
        }

        try:
            if isinstance(self.pms, PMS5003):
                sensor_data = self.pms.read()

                pms_data["smoke"] = sensor_data.pm_ug_per_m3(1.0)
                pms_data["metals"] = sensor_data.pm_ug_per_m3(2.5)
                pms_data["dust"] = sensor_data.pm_ug_per_m3(10)

                pms_data["mikro"] = sensor_data.pm_per_1l_air(0.3)
                pms_data["small"] = sensor_data.pm_per_1l_air(0.5)
                pms_data["medium"] = sensor_data.pm_per_1l_air(1.0)
        except Exception as e:
            self.main_logger.exception(e)

        return pms_data

    def get_data(self) -> dict[str, int]:
        return self._get_pms()
