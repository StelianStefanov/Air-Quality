import netifaces
from subprocess import PIPE, Popen

from src.main_config import main_cnf


class Utilities:

    @staticmethod
    def get_ip_address(net_interfaces) -> str:
        result = ""

        for name in net_interfaces:
            try:
                address = netifaces.ifaddresses(name)
                interfaces = address[netifaces.AF_INET]
                if interfaces:
                    result = interfaces[0]["addr"]
            except Exception:
                ...
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

            process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True)
            output, _error = process.communicate()

            return float(output[output.index("=") + 1 : output.rindex("'")])

        cpu_temps = [get_cpu_temperature()] * 5

        cpu_temp = get_cpu_temperature()
        # Smooth out with some averaging to decrease jitter
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

        return raw_temperature - ((avg_cpu_temp - raw_temperature) / factor)
