from celery import shared_task

from .utils import send_daily_hadith
from users.models import MainUser


@shared_task
def send_hadith():
    """ """
    users = MainUser.objects.all()
    for user in users:
        send_daily_hadith(user)
