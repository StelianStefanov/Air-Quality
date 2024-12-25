from bme280 import BME280
from smbus2 import SMBus
from pms5003 import PMS5003


class Sensor:
    def __init__(self):
        self.enviro = None
        self.pms = None

        try:
            self.enviro = BME280(i2c_dev=SMBus(1))
        except Exception:
            ...

        try:
            self.pms = PMS5003(device="/dev/ttyAMA0", baudrate=9600)
        except Exception:
            ...

    def _get_enviro(self):
        enviro_data = {
            "temperature": 0,
            "pressure": 0,
            "humidity": 0,
        }

        try:
            if isinstance(self.enviro, BME280):
                enviro_data["temperature"] = self.enviro.get_temperature()
                enviro_data["pressure"] = self.enviro.get_pressure()
                enviro_data["humidity"] = self.enviro.get_humidity()
        except Exception:
            ...

        return enviro_data

    def _get_pms(self):
        pms_data = {"pms": 0}

        try:
            if isinstance(self.pms, PMS5003):
                pms_data["pms"] = self.pms.read().pm_ug_per_m3(1.0)
        except Exception:
            ...

        return pms_data

    def get_data(self) -> dict[str, int]:
        enviro_data = self._get_enviro()
        pms_data = self._get_pms()

        return {**enviro_data, **pms_data}
