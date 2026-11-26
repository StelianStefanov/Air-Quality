from netifaces import interfaces, ifaddresses, AF_INET
from subprocess import CalledProcessError, TimeoutExpired, run
import json
import logging
import math
import re
import time

from src.main_config import main_cnf


class Utilities:
    # Each service supplies its configured logger at startup. Importing utilities
    # must not open a log file or configure application logging.
    logger = logging.getLogger("Air.utilities")

    @staticmethod
    def get_ip_address() -> str:
        """Gets the current ip address of the device"""

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

        timeout = main_cnf.cpu_temperature_timeout
        try:
            # run() kills and reaps the child if the timeout expires.
            result = run(
                ["vcgencmd", "measure_temp"],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout,
            )
            match = re.fullmatch(r"temp=(-?\d+(?:\.\d+)?)'C", result.stdout.strip())
            if match is None:
                raise ValueError("Invalid CPU temperature response")
            cpu_temp = float(match.group(1))
            if not math.isfinite(cpu_temp):
                raise ValueError("Invalid CPU temperature response")
        except (OSError, CalledProcessError, TimeoutExpired, ValueError) as error:
            Utilities.logger.exception(error)
            return raw_temperature

        factor = 2
        return raw_temperature - ((cpu_temp - raw_temperature) / factor)

    @staticmethod
    def read_sensor_shared_data(logger: logging.Logger) -> dict:
        while True:
            try:
                with open("/dev/shm/sensors_memory", "r") as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                logger.exception(e)
                time.sleep(0.5)

    @staticmethod
    def get_overall_quality(enviro_data: dict, pms_data: dict, enviro_gas_data: dict) -> str:
        """Get overall air quality with proper error handling"""

        GREEN_RANGE_THRESHOLD = 1028  # 12342 - number without deviding by 12
        YELLOW_RANGE_THRESHOLD = 3483  # 41805 - number without deviding by 12

        total_quality = ""
        try:
            total_quality = (
                + enviro_data["pressure"]
                + enviro_data["humidity"]
                + pms_data["smoke"]
                + pms_data["metals"]
                + pms_data["dust"]
                + pms_data["mikro"]
                + pms_data["small"]
                + pms_data["medium"]
                + enviro_gas_data["oxide"]
                + enviro_gas_data["reduce"]
                + enviro_gas_data["nh3"]
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
