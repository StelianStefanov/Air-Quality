#!/bin/bash
cd /home/pi/air_quality && source .venv/bin/activate && fastapi run www.py --host 0.0.0.0 --port 8000


