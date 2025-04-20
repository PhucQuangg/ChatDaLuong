import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns
from chat.AuthMiddleware import JWTAuthMiddleware  

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_backend.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(  
        URLRouter(websocket_urlpatterns)
    ),
})
