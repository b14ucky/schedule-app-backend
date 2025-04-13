#! /usr/bin/bash

IS_PRODUCTION=$(echo "$PRODUCTION" | tr -d '\r' | xargs)

if [ "$IS_PRODUCTION" = "true" ]; then
    echo "INFO: Running in production"
    sleep 10 && python manage.py migrate && uvicorn schedule_app.asgi:application --host 0.0.0.0 --port 8000

else
    echo "WARN: PRODUCTION is set to false, make sure you're not running this in production"
    sleep 10 && python manage.py migrate && uvicorn schedule_app.asgi:application --host 0.0.0.0 --port 8000 --reload

fi