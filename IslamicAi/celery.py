#!/usr/bin/env python3

"""Celery configuration"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import django

# os.environ['DJANGO_SETTINGS_MODULE'] = os.getenv('DJANGO_SETTINGS_MODULE', 'RentEase.settings.dev')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IslamicAi.settings')
# CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
django.setup()
app = Celery('IslamicAi')
app.conf.beat_schedule = {
    'send-daily-hadith': {
        'task': 'utils.tasks.send_hadith',
        'schedule': crontab(hour=12, minute=5),
    },
}
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(["utils"])
app.conf.update(
    task_track_started=True,
    loglevel='DEBUG',
)
print(app.conf.broker_url)
app.conf.broker_connection_max_retry_on_startup = True

if __name__ == '__main__':
    app.start()
