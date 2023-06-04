#!/bin/bash

# Start Gunicorn processes
#echo Starting Gunicorn.
#exec gunicorn --reload mainApi.app:app   -k uvicorn.workers.UvicornWorker  --bind 0.0.0.0:8000

# Start Gunicorn processes
echo Starting Uvicorn.
exec uvicorn --reload mainApi.app.main:app --host 0.0.0.0 --port 8000