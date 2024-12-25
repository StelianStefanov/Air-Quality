from pms5003 import PMS5003


class PmsSensor:
    def __init__(self):
        self.pms = None

        try:
            self.pms = PMS5003(device="/dev/ttyAMA0", baudrate=9600)
        except Exception:
            ...

    def _get_pms(self):
        pms_data = {"pms": 0}

        try:
            if isinstance(self.pms, PMS5003):
                pms_data["pms"] = self.pms.read().pm_ug_per_m3(1.0)
        except Exception:
            ...

        return pms_data

    def get_data(self) -> dict[str, int]:
        return self._get_pms()
