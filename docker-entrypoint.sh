#!/usr/bin/env bash
set -e

case "$1" in
    api)
        pipenv run python -m alembic upgrade head
        pipenv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
esac