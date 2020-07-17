from channels.routing import ProtocolTypeRouter, URLRouter
import echo.routing

application = ProtocolTypeRouter({
    "websocket": URLRouter(echo.routing.websocket_urlpatterns),
})
