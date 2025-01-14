from netifaces import interfaces, ifaddresses, AF_INET
from subprocess import PIPE, Popen
import orjson
import logging

from src.main_config import main_cnf
from src.logger import Logger


class Utilities:
    logger = Logger(logger_name="Air", level=logging.INFO, filename=str(main_cnf.cli_log_path))

    @staticmethod
    def get_ip_address() -> str:
        try:
            result = ""
            addresses = []
            for ifaceName in interfaces():
                add_info = ifaddresses(ifaceName).setdefault(AF_INET, [{"addr": ""}])
                if add_info:
                    ip_address = add_info[0].get("addr")
                    if ip_address and ip_address != "127.0.0.1":
                        addresses.append(ip_address)
        except Exception as e:
            Utilities.logger.exception(e)

        if addresses:
            result = addresses[0]

        return result

    @staticmethod
    def temperature_compensation(raw_temperature) -> float:
        """The temperature from the sensor show unrealistic data,
        because the raspberry and the display are heating up the sensor.
        That's why here we execute a simple formula that is using the raspberry
        temp and the sensor temp."""

        factor = main_cnf.compensation_temp_factor

        def get_cpu_temperature() -> float:
            """Gets the raspberry pi CPU temperature"""
            try:
                process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True)
                output, _error = process.communicate()

                return float(output[output.index("=") + 1 : output.rindex("'")])
            except FileNotFoundError as e:
                Utilities.logger.exception(e)
                return None

        if get_cpu_temperature() is not None:
            cpu_temps = [get_cpu_temperature()] * 5

            cpu_temp = get_cpu_temperature()
            # Smooth out with some averaging to decrease jitter
            cpu_temps = cpu_temps[1:] + [cpu_temp]
            avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

            return raw_temperature - ((avg_cpu_temp - raw_temperature) / factor)
        else:
            return raw_temperature

    @staticmethod
    def get_overall_quality() -> str:
        """Get overall air quality with proper error handling"""

        GREEN_RANGE_THRESHOLD = 1028  # 12342 - number without deviding by 12
        YELLOW_RANGE_THRESHOLD = 3483  # 41805 - number without deviding by 12

        def read_json() -> None:
            try:
                with open("/dev/shm/sensors_memory", "r") as f:
                    data = orjson.loads(f.read())
                    return data
            except Exception as e:
                Utilities.logger.exception(e)

        data = read_json()
        total_quality = ""
        try:
            total_quality = (
                data["temperature"]
                + data["pressure"]
                + data["humidity"]
                + data["smoke"]
                + data["metals"]
                + data["dust"]
                + data["mikro"]
                + data["small"]
                + data["medium"]
                + data["oxide"]
                + data["reduce"]
                + data["nh3"]
            )
            total_quality /= 12

            if total_quality <= GREEN_RANGE_THRESHOLD:
                total_quality = " Good"
            elif total_quality > GREEN_RANGE_THRESHOLD:
                total_quality = " Normal"
            elif total_quality >= YELLOW_RANGE_THRESHOLD:
                total_quality = " Bad"
        except Exception as e:
            Utilities.logger.exception(e)

        return total_quality
