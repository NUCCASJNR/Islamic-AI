from celery import shared_task
from users.models import MainUser
from .utils import send_daily_hadith


@shared_task
def send_hadith():
    users = MainUser.objects.all()
    for user in users:
        send_daily_hadith(user)
