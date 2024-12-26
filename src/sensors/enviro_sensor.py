from bme280 import BME280
from smbus2 import SMBus


class EnviroSensor:
    def __init__(self):
        self.enviro = None

        try:
            self.enviro = BME280(i2c_dev=SMBus(1))
        except Exception:
            ...

    def _get_enviro(self) -> dict[str, int]:
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

    def get_data(self) -> dict[str, int]:
        return self._get_enviro()
