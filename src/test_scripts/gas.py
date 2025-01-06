import ads1015


class EnviroGas:
    def __init__(self):

        self.adc = None

        try:
            self.adc = ads1015.ADS1015(i2c_addr=0x49)
            self.adc_type = self.adc.detect_chip_type()
        except Exception as e:
            ...

    def _get_gas(self):
        gas_data = {
            "oxide": 0,
            "reduce": 0,
            "nh3": 0,
        }

        try:
            if isinstance(self.adc, ads1015.ADS1015):
                self.ox = self.adc.get_voltage("in0/gnd")
                self.red = self.adc.get_voltage("in1/gnd")
                self.nh3 = self.adc.get_voltage("in2/gnd")
        except Exception as e:
            print(e)

        gas_data["oxide"] = ((self.ox * 56000) / (3.3 - self.ox)) / 1000
        gas_data["reduce"] = ((self.red * 56000) / (3.3 - self.red)) / 1000
        gas_data["nh3"] = ((self.nh3 * 56000) / (3.3 - self.nh3)) / 1000

        return gas_data

    def get_data(self) -> dict[str, int]:
        return self._get_gas()


if __name__ == "__main__":
    gas = EnviroGas()
    print(gas.get_data())
