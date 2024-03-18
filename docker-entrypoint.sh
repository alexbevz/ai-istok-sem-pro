set -e

case "$1" in
    api)
        exec bash -c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app"
        ;;
        exec "$@"
esac