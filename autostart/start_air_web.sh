#!/bin/bash
cd /home/pi/air_quality && source .venv/bin/activate && ./.venv/bin/python -m uvicorn www:app --host 0.0.0.0 --port 8000 --workers 1 --limit-concurrency 32


