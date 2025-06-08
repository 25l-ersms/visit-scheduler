#!/bin/sh

if [ "$1" = "debug" ]; then
    poetry run uvicorn --reload visit_scheduler.app.main:app --port 8080 --host 0.0.0.0
elif [ "$1" = "run" ]; then
    uvicorn --workers "${UVICORN_WORKERS:=4}" visit_scheduler.app.main:app --port 8080 --host 0.0.0.0
elif [ "$1" = "run-https" ]; then
    set -u
    uvicorn --workers "${UVICORN_WORKERS:=4}" visit_scheduler.app.main:app --port 8080 --host 0.0.0.0 --ssl-keyfile "$SSL_KEYFILE" --ssl-certfile "$SSL_CERTFILE"
else
    echo "Usage:
    $0 (run|run-https|debug)"
    exit 1
fi
