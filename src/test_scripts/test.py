import logging
import time
import netifaces

from enviroplus import gas

import st7735
from bme280 import BME280
from smbus2 import SMBus
from pms5003 import PMS5003

from test_scripts.sensors import sensors

from rich.live import Live
from rich.table import Table
from rich import box
from rich.align import Align
from rich.layout import Layout

from test_scripts.sensor import Sensor

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
)


sensor = Sensor()
pms5003 = PMS5003(device="/dev/ttyAMA0", baudrate=9600)


def get_data_sensor():
    try:
        while True:
            data = pms5003.read()
            return data
    except KeyboardInterrupt:
        pass


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


def output_table():

    def generate_table():
        table = Table(box=None, show_edge=False)
        table.add_column("Enviorement", width=100)
        table.add_column("Air Quality", width=100)
        table.add_column("      Test", width=100)

        ip_address = get_ip()
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d/%m/%Y")

        for row in range(1):
            sensor_data = sensor.get_data()
            temperature = sensor_data["temperature"]
            pressure = sensor_data["pressure"]
            humidity = sensor_data["humidity"]

            data = get_data_sensor()

            table.add_row(
                f":fire: {temperature:05.2f}°C\n🌬️ {pressure:05.2f}hPa\n💧 {humidity:05.2f}%",
                f"PM1.0:{data.pm_ug_per_m3(1.0)}μg/m3\nPM2.5:{data.pm_ug_per_m3(2.5)}μg/m3\nPM10:{data.pm_ug_per_m3(10)}μg/m3",
                f"      Test\n      Test\n      Test",
            )

            header = Layout(name="header", size=3)
            header.split_row(
                Layout(Align(ip_address, align="left")),
                Layout(Align(current_time, align="center")),
                Layout(Align(current_date, align="right")),
            )

            layout = Layout()
            layout.split(
                header,
                Layout(table, ratio=1),
            )

        return layout

    with Live(generate_table(), refresh_per_second=1) as live:
        while True:
            time.sleep(1)
            live.update(generate_table())


def display_data(sensors=sensors, sensor_order=["Temperature", "Pressure", "Humidity"]):

    while True:
        try:

            temperature, pressure, humidity = get_data()

            ip = get_ip()
            if ip:
                logging.info(ip)
                time.sleep(2.5)

            for sensor in sensor_order:
                sensor_type = sensors.get(sensor)

                limits = sensor_type["limits"]
                colors = sensor_type["colors_range"]
                unit = sensor_type["unit"]

                if sensor == "Temperature":
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
                    raise ValueError(f"Unknown sensor type: {sensor}")

                logging.info(f"{sensor}: {display_text}")

                time.sleep(2.5)

        except ValueError as e:
            logging.error(e)


output_table()
# get_data_sensor()
# display_data()
