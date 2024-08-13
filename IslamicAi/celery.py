#!/usr/bin/env python3
"""Celery configuration"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

# os.environ['DJANGO_SETTINGS_MODULE'] = os.getenv('DJANGO_SETTINGS_MODULE', 'RentEase.settings.dev')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IslamicAi.settings")
app = Celery("IslamicAi")
app.conf.beat_schedule = {
    "send-daily-hadith": {
        "task": "utils.tasks.send_hadith",
        "schedule": crontab(hour=11, minute=34),  # 6:00 AM daily
    },
}
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["utils.tasks"])
app.conf.update(
    task_track_started=True,
    loglevel="DEBUG",
)

app.conf.broker_connection_max_retry_on_startup = True

if __name__ == "__main__":
    app.start()
