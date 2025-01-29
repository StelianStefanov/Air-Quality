import datetime
import json

from textual.app import App, ComposeResult
from textual.widgets import Static, Header


from src.footer import FooterLayout
from src.utilities import Utilities
from src.sensors.enviro_sensor import EnviroSensor
from src.sensors.pms_sensor import PmsSensor
from src.sensors.enviro_gas import EnviroGas
from src.main_config import main_cnf
from src.sensors.sensors_data_format import SensorsDataFormat
from src.logger import Logger


class Display(App):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "display.tcss"

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self.enviro_sensor = EnviroSensor(self.logger)
        self.pms_sensor = PmsSensor(self.logger)
        self.enviro_gas_sensor = EnviroGas(self.logger)
        self.data_formatter = SensorsDataFormat()

    def compose(self) -> ComposeResult:
        """Creates the Grid"""

        date = datetime.datetime.now().strftime("%x")
        yield Header(show_clock=True, name="Hello", icon=date, id="header")
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
        yield Static("_", classes="box", id="oxide")
        yield Static("_", classes="box", id="reduce")
        yield Static("_", classes="box", id="nh3")

    def on_mount(self) -> None:
        """Header settings"""
        self.title = main_cnf.get_screen_title

    def on_ready(self) -> None:
        """Calls the update function and sets the interval"""
        self.update()
        self.set_interval(2, self.update)

    def save_json(self, pms_data: dict, enviro_data: dict, enviro_gas_data: dict) -> None:
        """
        Saves sensor data to a shared memory file as a JSON byte stream.

        It saves the json into a shared file in the memory of the linux system.

        Args:
            pms_data (dict): Data collected from the PMS sensor.
            enviro_data (dict): Data collected from the Enviro sensor.
            enviro_gas_data (dict): Data collected from the EnviroGas sensor.
        """

        default_data = {
            "temperature": 0,
            "pressure": 0,
            "humidity": 0,
            "smoke": 0,
            "metals": 0,
            "dust": 0,
            "oxide": 0,
            "reduce": 0,
            "nh3": 0,
            "mikro": 0,
            "small": 0,
            "medium": 0,
        }

        try:
            data_to_write = json.dumps({**enviro_data, **pms_data, **enviro_gas_data})
        except Exception as e:
            data_to_write = json.dumps(default_data)

        try:
            with open("/dev/shm/sensors_memory", "w") as f:
                f.write(data_to_write)
        except Exception as e:
            self.logger.exception(e)

    def update(self) -> None:
        """Refreshes the data in the interval of 1 second."""

        enviro_data = self.enviro_sensor.get_data()
        pms_data = self.pms_sensor.get_data()
        enviro_gas_data = self.enviro_gas_sensor.get_data()
        compensated_temp = Utilities.temperature_compensation(enviro_data["temperature"])
        overall_quality = Utilities.get_overall_quality()
        network_ip = str(Utilities.get_ip_address())

        self.query_one("#temp").update(self.data_formatter.do_format("temperature", compensated_temp))
        self.query_one("#press").update(self.data_formatter.do_format("pressure", enviro_data["pressure"]))
        self.query_one("#humid").update(self.data_formatter.do_format("humidity", enviro_data["humidity"]))
        self.query_one("#smoke").update(self.data_formatter.do_format("smoke", pms_data["smoke"]))
        self.query_one("#metals").update(self.data_formatter.do_format("metals", pms_data["metals"]))
        self.query_one("#dust").update(self.data_formatter.do_format("dust", pms_data["dust"]))
        self.query_one("#mikro").update(self.data_formatter.do_format("mikro", pms_data["mikro"]))
        self.query_one("#small").update(self.data_formatter.do_format("small", pms_data["small"]))
        self.query_one("#medium").update(self.data_formatter.do_format("medium", pms_data["medium"]))
        self.query_one("#oxide").update(self.data_formatter.do_format("oxide", enviro_gas_data["oxide"]))
        self.query_one("#reduce").update(self.data_formatter.do_format("reduce", enviro_gas_data["reduce"]))
        self.query_one("#nh3").update(self.data_formatter.do_format("nh3", enviro_gas_data["nh3"]))
        if overall_quality == " Normal":
            self.query_one(
                "#footer_right_static"
            ).update(  # The network ip is thrown into the abyss, because that the terminal display library manages the position of text....
                f"{self.data_formatter.do_format('overall_quaility', overall_quality)}                                                                                            {network_ip}"
            )  # If the quality is normal, the ip is a bit to the left, beacause the word 'Normal' is longer...
        else:
            self.query_one(
                "#footer_right_static"
            ).update(  # The network ip is thrown into the abyss, because that the terminal display library manages the position of text....
                f"{self.data_formatter.do_format('overall_quaility', overall_quality)}                                                                                              {network_ip}"
            )
        if network_ip:
            self.save_json(pms_data, enviro_data, enviro_gas_data)
