#!/bin/sh

if [ "$1" = "debug" ]; then
    poetry run uvicorn --reload visit_scheduler.app.main:app --port 8080
elif [ "$1" = "run" ]; then
    uvicorn --workers "${UVICORN_WORKERS:=4}" visit_scheduler.app.main:app --port 8080
else
    echo "Usage:
    $0 (run|debug)"
    exit 1
fi