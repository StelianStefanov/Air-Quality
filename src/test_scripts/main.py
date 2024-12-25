import time
from bme280 import BME280
from smbus2 import SMBus
from pms5003 import PMS5003

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)
pms = PMS5003(device="/dev/ttyAMA0", baudrate=9600)
while True:
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    pms1 = pms.read()
    print(temperature, pressure, humidity, pms1)
    time.sleep(1)
