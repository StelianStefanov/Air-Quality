import datetime
import orjson

from textual.app import App, ComposeResult
from textual.widgets import Static, Header


from src.footer import FooterLayout
from src.utilities import Utilities
from src.sensors.enviro_sensor import EnviroSensor
from src.sensors.pms_sensor import PmsSensor
from src.main_config import main_cnf
from src.sensors.sensors_data_format import SensorsDataFormat


class Display(App):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "display.tcss"

    def __init__(self):
        super().__init__()
        self.enviro_sensor = EnviroSensor()
        self.pms_sensor = PmsSensor()
        self.data_formatter = SensorsDataFormat()

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

    def save_json(self, pms_data: dict, enviro_data: dict) -> None:
        default_data = {
            "temperature": 0,
            "pressure": 0,
            "humidity": 0,
            "smoke": 0,
            "metals": 0,
            "dust": 0,
            "mikro": 0,
            "small": 0,
            "medium": 0,
        }

        try:
            data_to_write = orjson.dumps({**enviro_data, **pms_data})
        except Exception as e:
            data_to_write = orjson.dumps(default_data)

        try:
            with open("/dev/shm/sensors_memory", "wb") as f:
                f.write(data_to_write)
        except Exception:
            ...

    def update(self) -> None:
        """Refreshes the data in the interval of 1 second."""

        enviro_data = self.enviro_sensor.get_data()
        pms_data = self.pms_sensor.get_data()
        compensated_temp = Utilities.temperature_compensation(enviro_data["temperature"])
        network_ip = str(Utilities.get_ip_address(main_cnf.get_net_interfaces))

        self.query_one("#temp").update(self.data_formatter.do_format("temperature", compensated_temp))
        self.query_one("#press").update(self.data_formatter.do_format("pressure", enviro_data["pressure"]))
        self.query_one("#humid").update(self.data_formatter.do_format("humidity", enviro_data["humidity"]))
        self.query_one("#smoke").update(self.data_formatter.do_format("smoke", pms_data["smoke"]))
        self.query_one("#metals").update(self.data_formatter.do_format("metals", pms_data["metals"]))
        self.query_one("#dust").update(self.data_formatter.do_format("dust", pms_data["dust"]))
        self.query_one("#mikro").update(self.data_formatter.do_format("mikro", pms_data["mikro"]))
        self.query_one("#small").update(self.data_formatter.do_format("small", pms_data["small"]))
        self.query_one("#medium").update(self.data_formatter.do_format("medium", pms_data["medium"]))
        self.query_one("#footer_right_static").update(network_ip)

        if network_ip:
            self.save_json(pms_data, enviro_data)
