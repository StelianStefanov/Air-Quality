from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.widgets import Header
from src.sensor import Sensor
from src.footer import FooterLayout
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

        date = datetime.datetime.now().strftime("%x")
        yield Header(show_clock=True, name="Hello", icon=date)
        yield FooterLayout(show_command_palette=False)
        yield Static("_", classes="box", id="temp")
        yield Static("_", classes="box", id="press")
        yield Static("_", classes="box", id="humid")
        yield Static("_", classes="box", id="first_pms")
        yield Static("_", classes="box")
        yield Static("_", classes="box")
        yield Static("_", classes="box")
        yield Static("_", classes="box")
        yield Static("_", classes="box")

    def on_mount(self) -> None:
        """Header settings"""
        self.title = "Air Quality"

    def on_ready(self) -> None:
        """Calls the update function and sets the interval"""
        self.update()
        self.set_interval(1, self.update)

    def update(self) -> None:
        """Refreshes the data in the interval of 1 second."""

        sensor_data = self.sensor.get_data()
        compensated_temp = Utilities.temperature_compensation(sensor_data["temperature"])

        self.query_one("#footer_right_static").update(str(Utilities.get_ip_address(["eth0", "wlan0", "enp60s0"])))
        self.query_one("#temp").update(f"{str(float(round(compensated_temp, 1)))}°C")
        self.query_one("#press").update(f"{str(float(round(sensor_data['pressure'], 1)))}HPa")
        self.query_one("#humid").update(f"{str(float(round(sensor_data['humidity'], 1)))}%")
        self.query_one("#first_pms").update(str(float(round(sensor_data["pms"], 1))))
