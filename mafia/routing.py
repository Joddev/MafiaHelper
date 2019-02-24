from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import game.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': SessionMiddlewareStack(
        URLRouter(
            game.routing.websocket_urlpatterns
        )
    ),
})