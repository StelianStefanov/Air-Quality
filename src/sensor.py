from bme280 import BME280
from smbus2 import SMBus
from pms5003 import PMS5003


class Sensor:
    def __init__(self):
        self.enviro = BME280(i2c_dev=SMBus(1))
        self.pms = PMS5003(device="/dev/ttyAMA0", baudrate=9600)

    def get_data(self):
        return {
            "temperature": self._get_temperature_data(),
            "pressure": self._get_pressure_data(),
            "humidity": self._get_humidity_data(),
            "pms": self._get_pms_data(),
        }

    def _get_temperature_data(self):
        return self.enviro.get_temperature()

    def _get_pressure_data(self):
        return self.enviro.get_pressure()

    def _get_humidity_data(self):
        return self.enviro.get_humidity()

    def _get_pms_data(self):
        pms_data = self.pms.read()
        return pms_data.pm_ug_per_m3(1.0)
