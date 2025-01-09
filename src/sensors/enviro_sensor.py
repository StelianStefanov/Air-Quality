from bme280 import BME280
from smbus2 import SMBus
from src.logger import Logger


class EnviroSensor:
    def __init__(self, main_logger: Logger):
        self.enviro = None
        self.main_logger = main_logger

        try:
            self.enviro = BME280(i2c_dev=SMBus(1))
        except Exception as e:
            self.main_logger.exception(e)

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
        except Exception as e:
            self.main_logger.exception(e)

        return enviro_data

    def get_data(self) -> dict[str, int]:
        return self._get_enviro()
