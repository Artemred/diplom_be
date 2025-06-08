import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diplom_be.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'DEV')

from configurations.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns)
})