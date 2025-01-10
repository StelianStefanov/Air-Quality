"""FastApi views"""

import json
import orjson
import logging


from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from src.main_config import main_cnf
from src.sensors.enviro_sensor import EnviroSensor
from src.sensors.pms_sensor import PmsSensor
from src.utilities import Utilities
from src.web.sensor_colors import SensorColors
from src.logger import Logger

logger = Logger(logger_name="Air", level=logging.INFO, filename=str(main_cnf.web_log_path))
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
        logger.exception(e)


def get_context():
    """View Context"""
    data = read_json()
    compensated_temp = Utilities.temperature_compensation(data["temperature"])
    date = datetime.now().strftime("%x")
    clock = datetime.now().strftime("%H:%M")
    assets_version = main_cnf.assets_version

    return {
        "sensor_data": {
            "temp": f"{round(compensated_temp, 1)}°C",
            "pressure": f"{round(data['pressure'], 1)}HPa",
            "humidity": f"{round(data['humidity'], 1)}%",
            "smoke": f"{data['smoke']}µg/m³",
            "metals": f"{data['metals']}µg/m³",
            "dust": f"{data['dust']}µg/m³",
            "oxide": f"{round(data['oxide'], 2)}K0",
            "reduce": f"{round(data['reduce'], 2)}K0",
            "nh3": f"{round(data['nh3'], 2)}K0",
            "mikro": f"{data['mikro']}/0.1L",
            "small": f"{data['small']}/0.1L",
            "medium": f"{data['medium']}/0.1L",
            "date": date,
            "clock": clock,
        },
        "sensor_properties": {
            "page_title": "Air Quality",
            "temp_color": SensorColors.temperature(compensated_temp),
            "pressure_color": SensorColors.pressure(data["pressure"]),
            "humidity_color": SensorColors.humidity(data["humidity"]),
            "smoke_color": SensorColors.smoke(data["smoke"]),
            "metals_color": SensorColors.metals(data["metals"]),
            "dust_color": SensorColors.dust(data["dust"]),
            "oxide_color": SensorColors.oxide(data["oxide"]),
            "reduce_color": SensorColors.reduce(data["reduce"]),
            "nh3_color": SensorColors.nh3(data["nh3"]),
            "mikro_color": SensorColors.mikro(data["mikro"]),
            "small_color": SensorColors.small(data["small"]),
            "medium_color": SensorColors.medium(data["medium"]),
            "assets_version": assets_version,
            "reload_interval": main_cnf.web_interval_reload,
        },
    }


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    """Home page view"""
    data = get_context()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            **data["sensor_data"],
            **data["sensor_properties"],
        },
    )


@app.get("/dev", response_class=HTMLResponse)
def page_dev(request: Request):
    """Dev page view"""
    logger.info("Dev page")
    context = {}
    return templates.TemplateResponse(
        request=request,
        name="dev.html",
        context=get_context(),
    )


@app.get("/api/air-data", response_class=HTMLResponse)
def air_data(request: Request):
    """Data API"""

    return JSONResponse(content=jsonable_encoder(get_context()["sensor_data"]))
