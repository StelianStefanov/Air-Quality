from enviroplus import gas


class EnviroGas:
    def __init__(self, main_logger):
        self.main_logger = main_logger
        self.gas = gas

    def get_data(self) -> dict[str, int]:
        """
        Reads the gas data from the sensor and returns a dict with the resistance of
        oxidising, reducing and NH3 gases.

        Returns:
            dict[str, int]: A dictionary with the gas data.
        """
        gas_data = {
            "oxide": 0,
            "reduce": 0,
            "nh3": 0,
        }

        try:
            reading = self.gas.read_all()
            gas_data["oxide"] = reading.oxidising / 1000
            gas_data["reduce"] = reading.reducing / 1000
            gas_data["nh3"] = reading.nh3 / 1000
        except Exception as e:
            self.main_logger.exception(e)

        return gas_data
