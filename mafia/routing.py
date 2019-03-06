from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import game.routing

ASGI_APPLICATION = "mafia.routing.application"

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': SessionMiddlewareStack(
        URLRouter(
            game.routing.websocket_urlpatterns
        )
    ),
})