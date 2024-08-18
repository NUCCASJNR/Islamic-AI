#!/bin/bash

# Start the Celery worker in the background
python3 manage.py celery_worker &

# Start the Django development server
python3 manage.py runserver
