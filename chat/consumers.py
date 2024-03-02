from json import dumps, loads
from typing import NoReturn, Optional

from channels.generic.websocket import AsyncWebsocketConsumer
from redis import asyncio as aioredis


class ConsumerMixin:
    async def accept(self):
        ...

    async def connect(self) -> NoReturn:
        await self.accept()


class Consumer(AsyncWebsocketConsumer, ConsumerMixin):
    """
    TODO: docstrings
    TODO: разбить интерфейс по другим интерфейсам. т.к это "класс бога"
    """

    redis = aioredis.Redis()

    class Meta:
        KEY = 'query'

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.__group_name: Optional[str] = None

    @property
    def group_name(self) -> str:
        if not self.__group_name:
            self.__group_name = str(hash((self.channel_name.strip('specific.'))))

        return self.__group_name

    @group_name.setter
    def group_name(self, value: str) -> NoReturn:
        self.__group_name: str = value

    async def disconnect(self, code: str) -> NoReturn:
        """
        TODO: отправить письмо собеседнику (если есть), что пользователь покинул чат
        """

        await self.redis.delete(self.Meta.KEY)

    async def receive(self, text_data: str = None, bytes_data: bytes = None) -> NoReturn:
        data: dict = loads(s=text_data) | self.__dict__

        message_type: str = data.get('type')

        match message_type:
            case 'search':
                await self.search(data=data)
            case 'message':
                await self.send_message(data=data)

    async def join_group(self, target: str, seeker: str) -> NoReturn:
        """
        TODO: отправить письмо собеседнику
        """

        self.group_name: str = str(hash((target.strip('specific.'))))

        for channel_name in (target, seeker):
            await self.channel_layer.group_add(
                group=self.group_name,
                channel=channel_name,

            )

        await self.redis.delete(self.Meta.KEY)

    @classmethod
    async def add_to_query(cls, *values: tuple) -> NoReturn:
        await cls.redis.rpush(cls.Meta.KEY, *values)

    async def search(self, data: dict) -> None:
        channel_names = await self.redis.lrange(name=self.Meta.KEY, start=0, end=0)
        channel_name = (channel_names[0].decode('UTF-8') if channel_names else None)
        user_channel_name = data.get('channel_name')  # channel name of the user who is connecting

        if channel_name:
            return await self.join_group(target=channel_name, seeker=user_channel_name)

        await self.add_to_query(user_channel_name)

    async def send_message(self, data: dict) -> NoReturn:
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'message',
                'message': data.get('message'),
            }
        )

    async def message(self, event):
        message = event['message']

        await self.send(
            text_data=dumps(
                dict(
                    message=message,

                )
            )
        )
