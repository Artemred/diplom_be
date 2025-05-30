from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>[0-9a-f\-]+)/$", consumers.ChatConsumer.as_asgi()),
    path("ws/chats/list/", consumers.ChatListConsumer.as_asgi()),
]