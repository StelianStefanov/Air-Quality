from pms5003 import PMS5003, ChecksumMismatchError, ReadTimeoutError
from src.logger import Logger


class _ManagedPMS5003(PMS5003):
    """Cleanup adapter for the pinned pms5003==1.0.1 driver.

    That version has no close API. Its constructor owns a serial connection
    and two (gpiod.LineRequest, offset) tuples. Keep this compatibility code
    isolated and review it when upgrading the driver.
    """

    def __init__(self, logger, **kwargs):
        self._cleanup_logger = logger
        self._serial = None
        self._pin_enable = None
        self._pin_reset = None
        try:
            super().__init__(**kwargs)
        except BaseException:
            self.close()
            raise

    def close(self) -> None:
        for attribute, method in (
            ("_serial", "close"),
            ("_pin_reset", "release"),
            ("_pin_enable", "release"),
        ):
            resource = getattr(self, attribute)
            if resource is None:
                continue
            if method == "release":
                resource = resource[0]
            try:
                getattr(resource, method)()
            except Exception as error:
                self._cleanup_logger.exception(error)
            else:
                setattr(self, attribute, None)


class PmsSensor:
    def __init__(self, main_logger: Logger):
        self.main_logger = main_logger
        self.pms = None

        try:
            self.pms = _ManagedPMS5003(self.main_logger, device="/dev/serial0", baudrate=9600)
        except Exception as e:
            self.main_logger.exception(e)

    def close(self) -> None:
        if self.pms is not None:
            self.pms.close()
            self.pms = None

    def _get_pms(self) -> dict[str, int]:
        """
        Retrieves particulate matter data from the PMS5003 sensor.

        Returns:
            dict[str, int]: A dictionary containing the particulate matter data
            with keys "smoke", "metals", "dust", "mikro", "small", and "medium".
        """

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
        except (ChecksumMismatchError, ReadTimeoutError) as e:
            #self.main_logger.exception(e)
            try:
                self.pms.reset()  # flushes buffer and re-syncs frame alignment
            except Exception:
                pass
        except Exception as e:
            self.main_logger.exception(e)

        return pms_data

    def get_data(self) -> dict[str, int]:
        return self._get_pms()
