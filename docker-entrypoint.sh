#!/usr/bin/env bash
set -e

case "$1" in
    api)
        python3.11 -m alembic upgrade head
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
esac
