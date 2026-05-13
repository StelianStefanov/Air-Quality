#!/bin/bash
cd /home/pi/air_quality && source .venv/bin/activate && ./.venv/bin/python -m fastapi run www.py --host 0.0.0.0 --port 8000 --reload


