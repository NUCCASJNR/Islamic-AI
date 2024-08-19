#!/bin/bash
# This script restarts Celery worker and beat
pkill -f "celery worker"
pkill -f "celery beat"
celery -A IslamicAi worker -l DEBUG --logfile=/var/log/celery/celery_worker.log &
celery -A IslamicAi beat -l DEBUG --logfile=/var/log/celery/celery_beat.log &
