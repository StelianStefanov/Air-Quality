"""FastApi views"""

import json
import orjson

from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.main_config import main_cnf
from src.sensors.enviro_sensor import EnviroSensor
from src.sensors.pms_sensor import PmsSensor
from src.utilities import Utilities
from src.web.sensor_colors import SensorColors


app = FastAPI()

STATIC_DIR = main_cnf.root_dir / "src/web/static"
TEMPLATES_DIR = main_cnf.root_dir / "src/web/templates"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


templates = Jinja2Templates(directory=TEMPLATES_DIR)


def read_json() -> None:
    try:
        with open("/dev/shm/sensors_memory", "r") as f:
            data = orjson.loads(f.read())
            return data
    except Exception as e:
        print(e)


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    """Home page view"""
    data = read_json()
    compensated_temp = Utilities.temperature_compensation(data["temperature"])
    date = datetime.now().strftime("%x")
    clock = datetime.now().strftime("%H:%M")
    assets_version = main_cnf.assets_version

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "temp": f"{round(compensated_temp, 1)}°C",
            "pressure": f"{round(data['pressure'], 1)}HPa",
            "humidity": f"{round(data['humidity'], 1)}%",
            "smoke": f"{data['smoke']}µg/m³",
            "metals": f"{data['metals']}µg/m³",
            "dust": f"{data['dust']}µg/m³",
            "mikro": f"{data['mikro']}/0.1L",
            "small": f"{data['small']}/0.1L",
            "medium": f"{data['medium']}/0.1L",
            "date": date,
            "clock": clock,
            "page_title": "Air Quality",
            "temp_color": SensorColors.temperature(compensated_temp),
            "pressure_color": SensorColors.pressure(data["pressure"]),
            "humidity_color": SensorColors.humidity(data["humidity"]),
            "smoke_color": SensorColors.smoke(data["smoke"]),
            "metals_color": SensorColors.metals(data["metals"]),
            "dust_color": SensorColors.dust(data["dust"]),
            "mikro_color": SensorColors.mikro(data["mikro"]),
            "small_color": SensorColors.small(data["small"]),
            "medium_color": SensorColors.medium(data["medium"]),
            "assets_version": assets_version,
        },
    )
