from django.urls import path

from . import consumers

urlpatterns = (
    path('ws/', consumers.Consumer.as_asgi()),
)
