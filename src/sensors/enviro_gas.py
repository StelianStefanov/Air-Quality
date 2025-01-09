import atexit
import time
from dataclasses import dataclass

import ads1015
import gpiod
from gpiod.line import Direction, Value

from src.logger import Logger

MICS6814_GAIN = 6.144

OUTH = gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.ACTIVE)

ads1015.I2C_ADDRESS_DEFAULT = ads1015.I2C_ADDRESS_ALTERNATE


@dataclass(slots=True)
class GasDataContainer:
    oxidising: float
    reducing: float
    nh3: float


class EnviroGas:
    def __init__(self, main_logger: Logger):
        self.main_logger = main_logger
        self._is_setup = False
        self._is_available = False
        self._adc_enabled = False
        self._adc_gain = MICS6814_GAIN
        self._heater = None
        self.adc = None
        self.adc_type = None

    # class Mics6814Reading:
    #     __slots__ = "oxidising", "reducing", "nh3", "adc"

    #     def __init__(self, ox, red, nh3, adc=None):
    #         self.oxidising = ox
    #         self.reducing = red
    #         self.nh3 = nh3
    #         self.adc = adc

    def _setup(self):
        if self._is_setup:
            return
        self._is_setup = True

        try:
            self.adc = ads1015.ADS1015(i2c_addr=0x49)
            self.adc_type = self.adc.detect_chip_type()
            self._is_available = True
        except IOError:
            self._is_available = False
            return

        self.adc.set_mode("single")
        self.adc.set_programmable_gain(MICS6814_GAIN)
        if self.adc_type == "ADS1115":
            self.adc.set_sample_rate(128)
        else:
            self.adc.set_sample_rate(1600)

        atexit.register(self._cleanup)

    def _available(self):
        self._setup()
        return self._is_available

    def _enable_adc(self, value=True):
        """Enable reading from the additional ADC pin."""
        self._adc_enabled = value

    def _set_adc_gain(self, value):
        """Set gain value for the additional ADC pin."""
        self._adc_gain = value

    def _cleanup(self):
        if self._heater is None:
            return
        lines, offset = self._heater
        lines.set_value(offset, Value.INACTIVE)

    def _read_all(self) -> GasDataContainer:
        """Return gas resistance for oxidising, reducing and NH3"""
        self._setup()

        if not self._is_available:
            raise RuntimeError("Gas sensor not connected.")

        ox = self.adc.get_voltage("in0/gnd")
        red = self.adc.get_voltage("in1/gnd")
        nh3 = self.adc.get_voltage("in2/gnd")

        try:
            ox = ((ox * 56000) / (3.3 - ox)) / 1000
        except ZeroDivisionError:
            ox = 0

        try:
            red = ((red * 56000) / (3.3 - red)) / 1000
        except ZeroDivisionError:
            red = 0

        try:
            nh3 = ((nh3 * 56000) / (3.3 - nh3)) / 1000
        except ZeroDivisionError:
            nh3 = 0

        # analog = None

        if self._adc_enabled:
            if self._adc_gain != MICS6814_GAIN:
                self.adc.set_programmable_gain(self._adc_gain)
                time.sleep(0.05)
                # analog = self.adc.get_voltage("ref/gnd")
                self.adc.set_programmable_gain(MICS6814_GAIN)

        return GasDataContainer(ox, red, nh3)

    def get_data(self) -> dict[str, int]:
        gas_data = {
            "oxide": 0,
            "reduce": 0,
            "nh3": 0,
        }

        try:
            reading = self._read_all()
            gas_data["oxide"] = reading.oxidising
            gas_data["reduce"] = reading.reducing
            gas_data["nh3"] = reading.nh3
        except Exception as e:
            self.main_logger.exception(e)

        return gas_data
