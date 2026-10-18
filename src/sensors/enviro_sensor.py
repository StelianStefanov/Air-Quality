from bme280 import BME280
from smbus2 import SMBus
from src.logger import Logger


class EnviroSensor:
    def __init__(self, main_logger: Logger):
        self.enviro = None
        self.bus = None
        self.main_logger = main_logger

        try:
            # Retain ownership even if open() or BME280 initialization fails.
            self.bus = SMBus()
            self.bus.open(1)
            self.enviro = BME280(i2c_dev=self.bus)
        except Exception as e:
            self.main_logger.exception(e)
            self.close()
        except BaseException:
            self.close()
            raise

    def close(self) -> None:
        self.enviro = None
        if self.bus is not None:
            try:
                self.bus.close()
            except Exception as error:
                self.main_logger.exception(error)
            else:
                self.bus = None

    def _get_enviro(self) -> dict[str, int]:
        """
        Retrieves environmental data from the BME280 sensor.

        Returns:
            dict[str, int]: A dictionary containing the temperature, pressure,
                            and humidity readings.
        """

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
