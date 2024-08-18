#!/bin/bash

# Start the Celery worker in the background
python3 manage.py celery_worker &

# Check if PORT is set and not empty
if [ -n "$PORT" ]; then
  gunicorn IslamicAi.wsgi:application --bind 0.0.0.0:$PORT
else
  python3 manage.py runserver
fi
