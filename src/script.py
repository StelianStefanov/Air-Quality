import logging
import time
import netifaces

from enviroplus import gas

import st7735
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont

from bme280 import BME280
from smbus2 import SMBus

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info(
    """Print readings from the BME280 weather sensor.

Press Ctrl+C to exit!

"""
)

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)


def get_data():
    """Fetch temperature, pressure, and humidity from the BME280 sensor."""
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    return temperature, pressure, humidity


display = st7735.ST7735(port=0, cs=1, dc="GPIO9", backlight="GPIO12", rotation=270, spi_speed_hz=10000000)


inter_names = ["eth0", "wlan0"]


def get_ip():
    result = None

    for name in inter_names:
        try:
            address = netifaces.ifaddresses(name)
            interfaces = address[netifaces.AF_INET]
            if interfaces:
                result = interfaces[0]["addr"]
        except Exception:
            ...

    return result


def display_data():

    # Start display
    display.begin()

    WIDTH = display.width
    HEIGHT = display.height

    # New canvas to draw on.
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Text settings.
    font_size = 25
    font = ImageFont.truetype(UserFont, font_size)
    text_colour = (255, 255, 255)
    back_colour = (0, 0, 0)

    # Main Loop
    while True:

        temperature, pressure, humidity = get_data()

        # IP
        ip = get_ip()
        if ip:
            draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
            font_ip = ImageFont.truetype(UserFont, 18)
            draw.text((15, 25), ip, font=font_ip, fill=text_colour)
            display.display(img)
            time.sleep(5)

        # NH3(Amonia)
        readings = gas.read_all()
        readings_text = f"{readings.nh3 / 1000:05.2f} kO"
        draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
        if readings.nh3 > 0 and readings.nh3 < 100:
            text_colour = (0, 255, 255)
        elif readings.nh3 > 100 and readings.nh3 < 150:
            text_colour = (179, 209, 46)
        elif readings.nh3 > 150 and readings.nh3 < 200:
            text_colour = (255, 255, 0)
        elif readings.nh3 > 200 and readings.nh3 < 250:
            text_colour = (255, 145, 0)
        elif readings.nh3 > 250 and readings.nh3 < 300:
            text_colour = (255, 0, 0)
        elif readings.nh3 > 300 and readings.nh3 < 1000:
            text_colour = (77, 0, 0)
        draw.text((20, 25), readings_text, font=font, fill=text_colour)
        display.display(img)
        logging.info(f"NH3:{readings_text}")
        time.sleep(2.5)

        # Temperature
        temperature -= 3
        temperature_text = f"{temperature:05.2f}°C"
        draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
        if temperature < 15:
            text_colour = (0, 255, 255)
        elif temperature > 15 and temperature < 20:
            text_colour = (179, 209, 46)
        elif temperature > 20 and temperature < 25:
            text_colour = (0, 255, 0)
        elif temperature > 25 and temperature < 30:
            text_colour = (255, 145, 0)
        elif temperature > 30:
            text_colour = (255, 0, 0)
        draw.text((40, 25), temperature_text, font=font, fill=text_colour)
        display.display(img)
        logging.info(f"Temperature: {temperature_text}")
        time.sleep(2.5)

        # Pressure
        pressure_text = f"{pressure:05.2f} hPa"
        draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
        if pressure < 1000:
            text_colour = (0, 255, 255)
        elif pressure > 1013:
            text_colour = (255, 255, 0)
        elif pressure > 1030:
            text_colour = (255, 0, 0)
        draw.text((17, 25), pressure_text, font=font, fill=text_colour)
        display.display(img)
        logging.info(f"Pressure: {pressure_text}")
        time.sleep(2.5)

        # Humidity
        humidity_text = f"{humidity:05.2f} %"
        draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
        if humidity < 30:
            text_colour = (0, 255, 2555)
        elif humidity > 30 and humidity < 60:
            text_colour = (255, 255, 0)
        elif humidity > 60:
            text_colour = (255, 0, 0)
        draw.text((40, 25), humidity_text, font=font, fill=text_colour)
        display.display(img)
        logging.info(f"Humidity: {humidity_text}")
        time.sleep(2.5)


# Temporary main runner
try:
    display_data()
except KeyboardInterrupt:
    display.set_backlight(0)
