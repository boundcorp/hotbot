#!/usr/bin/env bash

/app/.venv/bin/python3 manage.py migrate
/app/.venv/bin/uvicorn \
    hotbot.main:app \
    --host 0.0.0.0 \
    --port 8000