#!/usr/bin/env bash
set -e

exec pipenv shell -c "alembic upgrade head"

case "$1" in
    api)
        exec pipenv shell -c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app"
        ;;
        exec "$@"
esac