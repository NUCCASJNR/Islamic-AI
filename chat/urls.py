from django.urls import path

from .api import chat

urlpatterns = [
    path("", chat.urls),
]
