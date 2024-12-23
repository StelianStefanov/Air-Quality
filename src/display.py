from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.widgets import Label, Digits, Header
from src.sensor import Sensor
import random
import datetime
from src.utilities import Utilities


class Display(App):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "display.tcss"

    def __init__(self):
        super().__init__()
        self.sensor = Sensor()

    def compose(self) -> ComposeResult:
        """Creates the Grid"""

        date = datetime.datetime.now().strftime('%x')
        yield Header(show_clock=True, name="Hello", icon=date)
        yield Static("_", classes="box", id="temp")
        # yield Label("Hello, world!", classes="box")
        yield Static("_", classes="box", id="press")
        # yield Static("Three", classes="box")
        yield Static("_", classes="box", id="humid")
        yield Static("_", classes="box", id="first_pms")
        yield Static("_", classes="box")
        yield Static("_", classes="box")
        yield Static("_", classes="box")
        yield Static("_", classes="box")
        yield Static("_", classes="box")

    def on_mount(self) -> None:
        """Header settings"""
        self.title = "Header Application"

    def on_ready(self) -> None:
        """Calls the update function and sets the interval
        """
        self.update()
        self.set_interval(1, self.update)

    def update(self) -> None:
        """Refreshes the data in the interval of 1 second."""

        sensor_data = self.sensor.get_data()
        # compensated_temp = Utilities.temperature_compensation(
        # sensor_data["temperature"])
        self.title = Utilities.get_ip_address(
            ["eth0", "wlan0", "enp60s0"])
        # self.query_one("#temp").update(str(compensated_temp))
        self.query_one("#temp").update(str(sensor_data["temperature"]))
        self.query_one("#press").update(str(sensor_data["pressure"]))
        self.query_one("#humid").update(str(sensor_data["humidity"]))
        self.query_one("#first_pms").update(str(sensor_data["pms"]))
