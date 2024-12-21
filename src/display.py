from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.widgets import Label
from textual.widgets import Digits
from src.sensor import Sensor
import random


class Display(App):

    CSS_PATH = "display.tcss"

    def __init__(self):
        super().__init__()
        self.sensor = Sensor()

    def compose(self) -> ComposeResult:

        yield Static(f"", classes="box some", id="f")
        # yield Label("Hello, world!", classes="box")
        yield Static("Two", classes="box", id="s")
        # yield Static("Three", classes="box")
        yield Static("454545", classes="box", id="st")
        yield Static("Temp: 16C", classes="box", id="temp")
        yield Static("Five", classes="box")
        yield Static("Six", classes="box")
        yield Static("Seven", classes="box")
        yield Static("8888", classes="box")
        yield Static("9999", classes="box")

    def on_ready(self) -> None:
        self.update()
        self.set_interval(1, self.update)

    def update(self):
        sensor_data = self.sensor.get_data()

        self.query_one("#f").update(str(sensor_data["temperature"]))
        self.query_one("#st").update(str(sensor_data["pms"]))
        # self.query_one("#temp").update(f"Temp: {random.randint(1, 30)}C")
