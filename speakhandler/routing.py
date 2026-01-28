from django.urls import path, re_path
from .consumers import ChatConsumer


websocket_urlpatterns = [
    re_path(r'ws/notification/(?P<room_name>[^/]+)/(?P<language>[^/]+)/$', ChatConsumer.as_asgi()),
]