from django.urls import re_path

from .consumers import MessageConsumer


websocket_urlpatterns = [
    re_path(r"ws/chat/c/(?P<chat_id>[\w-]+)/$", MessageConsumer.as_asgi()),
]
