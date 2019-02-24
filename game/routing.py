from django.conf.urls import url

from game.socket import consumers

websocket_urlpatterns = [
    url(r'^ws/$', consumers.GameConsumer),
]