import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    """ """
    # Kill any running celery worker processes
    cmd = 'pkill -f "celery worker"'
    subprocess.call(shlex.split(cmd))

    # Kill any running celery beat processes
    cmd = 'pkill -f "celery beat"'
    subprocess.call(shlex.split(cmd))

    # Start the Celery worker and beat in separate subprocesses
    worker_cmd = "celery -A IslamicAi worker -l DEBUG --logfile=celery_worker.log"
    beat_cmd = "celery -A IslamicAi beat -l DEBUG --logfile=celery_beat.log"

    subprocess.Popen(shlex.split(worker_cmd))
    subprocess.Popen(shlex.split(beat_cmd))


class Command(BaseCommand):
    """ """
    def handle(self, *args, **options):
        """

        :param *args: 
        :param **options: 

        """
        print("Starting celery worker and beat with autoreload...")
        autoreload.run_with_reloader(restart_celery)
