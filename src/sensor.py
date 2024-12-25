from bme280 import BME280
from smbus2 import SMBus
from pms5003 import PMS5003


class Sensor:
    def __init__(self):
        self.enviro = BME280(i2c_dev=SMBus(1))
        self.pms = PMS5003(device="/dev/ttyAMA0", baudrate=9600)

    def get_data(self) -> dict[str, int]:
        """Fetches data from BME280 and PMS5003 sensors"""

        default_data = {
            "temperature": 0,
            "pressure": 0,
            "humidity": 0,
            "pms": 0,
        }

        try:

            default_data["temperature"] = self.enviro.get_temperature()
            default_data["pressure"] = self.enviro.get_pressure()
            default_data["humidity"] = self.enviro.get_humidity()

            pms_data = self.pms.read()
            default_data["pms"] = pms_data.pm_ug_per_m3(1.0)

        except PermissionError:
            ...

        return default_data


if __name__ == "__main__":
    sensor = Sensor()
    while True:
        print(sensor.get_data())
