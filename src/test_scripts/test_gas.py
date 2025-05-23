"""Read the MICS6814 via an ads1015 ADC"""

import atexit
import time

import ads1015
import gpiod
import gpiodevice
from gpiod.line import Direction, Value

MICS6814_GAIN = 6.144

OUTH = gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.ACTIVE)


ads1015.I2C_ADDRESS_DEFAULT = ads1015.I2C_ADDRESS_ALTERNATE
_is_setup = False
_is_available = False
_adc_enabled = False
_adc_gain = 6.148
_heater = None


class Mics6814Reading(object):
    __slots__ = "oxidising", "reducing", "nh3", "adc"

    def __init__(self, ox, red, nh3, adc=None):
        self.oxidising = ox
        self.reducing = red
        self.nh3 = nh3
        self.adc = adc

    def __repr__(self):
        fmt = f"""Oxidising: {self.oxidising:05.02f} Ohms
Reducing: {self.reducing:05.02f} Ohms
NH3: {self.nh3:05.02f} Ohms"""
        if self.adc is not None:
            fmt += f"""
ADC: {self.adc:05.02f} Volts
"""
        return fmt

    __str__ = __repr__


def setup():
    global adc, adc_type, _is_setup, _is_available, _heater
    if _is_setup:
        return
    _is_setup = True

    try:
        adc = ads1015.ADS1015(i2c_addr=0x49)
        adc_type = adc.detect_chip_type()
        _is_available = True
    except IOError:
        _is_available = False
        return

    adc.set_mode("single")
    adc.set_programmable_gain(MICS6814_GAIN)
    if adc_type == "ADS1115":
        adc.set_sample_rate(128)
    else:
        adc.set_sample_rate(1600)

    # _heater = gpiodevice.get_pin("GPIO24", "EnviroPlus", OUTH)

    atexit.register(cleanup)


def available():
    setup()
    return _is_available


def enable_adc(value=True):
    """Enable reading from the additional ADC pin."""
    global _adc_enabled
    _adc_enabled = value


def set_adc_gain(value):
    """Set gain value for the additional ADC pin."""
    global _adc_gain
    _adc_gain = value


def cleanup():
    if _heater is None:
        return
    lines, offset = _heater
    lines.set_value(offset, Value.INACTIVE)


def read_all():
    """Return gas resistance for oxidising, reducing and NH3"""
    setup()

    if not _is_available:
        raise RuntimeError("Gas sensor not connected.")

    ox = adc.get_voltage("in0/gnd")
    red = adc.get_voltage("in1/gnd")
    nh3 = adc.get_voltage("in2/gnd")

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

    analog = None

    if _adc_enabled:
        if _adc_gain == MICS6814_GAIN:
            analog = adc.get_voltage("ref/gnd")
        else:
            adc.set_programmable_gain(_adc_gain)
            time.sleep(0.05)
            analog = adc.get_voltage("ref/gnd")
            adc.set_programmable_gain(MICS6814_GAIN)

    return Mics6814Reading(ox, red, nh3, analog)


def read_oxidising():
    """Return gas resistance for oxidising gases.

    Eg chlorine, nitrous oxide
    """
    return read_all().oxidising


def read_reducing():
    """Return gas resistance for reducing gases.

    Eg hydrogen, carbon monoxide
    """
    return read_all().reducing


def read_nh3():
    """Return gas resistance for nh3/ammonia"""
    return read_all().nh3


def read_adc():
    """Return spare ADC channel value"""
    return read_all().adc


print(read_nh3())
