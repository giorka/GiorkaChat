from os import environ

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from chat.routing import urlpatterns

environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter(
    dict(
        http=get_asgi_application(),
        ws=URLRouter(
            urlpatterns
        )
    )
)
