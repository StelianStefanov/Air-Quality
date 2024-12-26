import random
import datetime

from textual.app import App, ComposeResult
from textual.widgets import Static, Header


from src.footer import FooterLayout
from src.utilities import Utilities
from src.sensors.enviro_sensor import EnviroSensor
from src.sensors.pms_sensor import PmsSensor
from src.main_config import main_cnf


class Display(App):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "display.tcss"

    def __init__(self):
        super().__init__()
        self.enviro_sensor = EnviroSensor()
        self.pms_sensor = PmsSensor()

    def compose(self) -> ComposeResult:
        """Creates the Grid"""

        date = datetime.datetime.now().strftime("%x")
        yield Header(show_clock=True, name="Hello", icon=date)
        yield FooterLayout(show_command_palette=False)
        yield Static("_", classes="box", id="temp")
        yield Static("_", classes="box", id="smoke")
        yield Static("_", classes="box", id="mikro")
        yield Static("_", classes="box", id="press")
        yield Static("_", classes="box", id="metals")
        yield Static("_", classes="box", id="small")
        yield Static("_", classes="box", id="humid")
        yield Static("_", classes="box", id="dust")
        yield Static("_", classes="box", id="medium")

    def on_mount(self) -> None:
        """Header settings"""
        self.title = main_cnf.get_screen_title

    def on_ready(self) -> None:
        """Calls the update function and sets the interval"""
        self.update()
        self.set_interval(1, self.update)

    def update(self) -> None:
        """Refreshes the data in the interval of 1 second."""

        enviro_data = self.enviro_sensor.get_data()
        pms_data = self.pms_sensor.get_data()
        compensated_temp = Utilities.temperature_compensation(enviro_data["temperature"])

        self.query_one("#footer_right_static").update(str(Utilities.get_ip_address(main_cnf.get_net_interfaces)))
        self.query_one("#temp").update(f"Temp: {str(float(round(compensated_temp, 1)))}°C")
        self.query_one("#press").update(f"Pressure: {str(float(round(enviro_data['pressure'], 1)))}HPa")
        self.query_one("#humid").update(f"Humidity: {str(float(round(enviro_data['humidity'], 1)))}%")
        self.query_one("#smoke").update(f"Smoke: {str(int(pms_data['smoke']))}µg/m³")
        self.query_one("#metals").update(f"Metals: {str(int(pms_data['metals']))}µg/m³")
        self.query_one("#dust").update(f"Dust: {str(int(pms_data['dust']))}µg/m³")
        self.query_one("#mikro").update(f"Mikro: {str(int((pms_data['mikro'])))}/0.1L")
        self.query_one("#small").update(f"Small: {str(int(pms_data['small']))}/0.1L")
        self.query_one("#medium").update(f"Medium: {str(int((pms_data['medium'])))}/0.1L")
