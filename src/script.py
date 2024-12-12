import logging
import time
import netifaces

from enviroplus import gas

import st7735
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont

from bme280 import BME280
from smbus2 import SMBus

from src.sensors import sensors

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
    try:
        temperature = bme280.get_temperature()
        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()
        return temperature, pressure, humidity
    except Exception:
        logging.exception("Error getting data from the BME280(This is the white board with the screen) sensor")


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


def display_data(sensors=sensors, sensor_order=["NH3", "Temperature", "Pressure", "Humidity"]):
    display.begin()

    WIDTH = display.width
    HEIGHT = display.height

    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_size = 25
    font = ImageFont.truetype(UserFont, font_size)
    font_ip = ImageFont.truetype(UserFont, 18)  # Load IP font once
    text_colour = (255, 255, 255)
    back_colour = (0, 0, 0)

    while True:
        try:

            temperature, pressure, humidity = get_data()

            ip = get_ip()
            if ip:
                draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
                draw.text((15, 25), ip, font=font_ip, fill=text_colour)
                display.display(img)
                logging.info(ip)
                time.sleep(2.5)

            for sensor in sensor_order:
                sensor_type = sensors.get(sensor)

                limits = sensor_type["limits"]
                colors = sensor_type["colors_range"]
                unit = sensor_type["unit"]
                text_position = sensor_type["text_position"]

                display_text = ""

                if sensor == "NH3":
                    readings = gas.read_all()
                    nh3_value = readings.nh3 / 1000
                    display_text = f"{nh3_value:05.2f} {unit}"

                    # Color of the text depending on the value
                    if limits[0] <= readings.nh3 < limits[1]:
                        text_colour = colors["light_blue"]
                    elif limits[1] <= readings.nh3 < limits[2]:
                        text_colour = colors["yellow"]
                    elif limits[2] <= readings.nh3 < limits[3]:
                        text_colour = colors["darker_yellow"]
                    elif limits[3] <= readings.nh3 < limits[4]:
                        text_colour = colors["orange"]
                    elif limits[4] <= readings.nh3 < limits[5]:
                        text_colour = colors["red"]
                    elif readings.nh3 >= limits[5]:
                        text_colour = colors["dark_red"]

                elif sensor == "Temperature":
                    temperature -= 3  # The raspberry pi is warming up the sensor a bit, so I substracted it.
                    display_text = f"{temperature:05.2f} {unit}"

                    # Color of the text depending on the value
                    if temperature < limits[0]:
                        text_colour = colors["light_blue"]
                    elif limits[0] <= temperature < limits[1]:
                        text_colour = colors["yellow"]
                    elif limits[1] <= temperature < limits[2]:
                        text_colour = colors["green"]
                    elif limits[2] <= temperature < limits[3]:
                        text_colour = colors["orange"]
                    elif temperature >= limits[3]:
                        text_colour = colors["red"]

                elif sensor == "Pressure":
                    display_text = f"{pressure:05.2f} {unit}"

                    # Color of the text depending on the value
                    if pressure < limits[0]:
                        text_colour = colors["light_blue"]
                    elif limits[0] <= pressure < limits[1]:
                        text_colour = colors["yellow"]
                    elif pressure >= limits[2]:
                        text_colour = colors["red"]

                elif sensor == "Humidity":
                    display_text = f"{humidity:05.2f} {unit}"

                    # Color of the text depending on the value
                    if humidity < limits[0]:
                        text_colour = colors["light_blue"]
                    elif limits[0] <= humidity < limits[1]:
                        text_colour = colors["yellow"]
                    elif humidity >= limits[1]:
                        text_colour = colors["red"]

                else:
                    display.set_backlight(0)
                    raise ValueError(f"Unknown sensor type: {sensor}")

                draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
                draw.text(text_position, display_text, font=font, fill=text_colour)
                display.display(img)
                logging.info(f"{sensor}: {display_text}")

                time.sleep(2.5)

        except ValueError as e:
            logging.error(e)


def old_display_data():

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
