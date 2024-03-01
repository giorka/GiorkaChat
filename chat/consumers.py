from typing import NoReturn

from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
    async def connect(self) -> NoReturn:
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        ...
