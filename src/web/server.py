"""FastApi views"""
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.main_config import main_cnf
app = FastAPI()

STATIC_DIR = main_cnf.root_dir / "src/web/static"
TEMPLATES_DIR = main_cnf.root_dir / "src/web/templates"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    """Home page view"""

    return templates.TemplateResponse(
        request=request, name="index.html", context={
            "num1": random.randint(1, 10000),
            "num2": random.randint(1, 100)
        }
    )
