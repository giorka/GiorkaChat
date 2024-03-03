from abc import ABC, abstractmethod
from json import dumps, loads
from typing import NoReturn, Optional

from channels.generic.websocket import AsyncWebsocketConsumer

from . import mixins


def clear_queues(function: callable) -> callable:
    async def wrapper(*args, **kwargs) -> NoReturn:
        print(mixins.RedisConsumerMixin.Meta.KEY)
        await mixins.RedisConsumerMixin.redis.delete(mixins.RedisConsumerMixin.Meta.KEY)
        return await function(*args, **kwargs)

    return wrapper


class AbstractConsumer(ABC, AsyncWebsocketConsumer):
    @abstractmethod
    async def receive(self, text_data: str = None, bytes_data: bytes = None) -> NoReturn:
        ...

    @abstractmethod
    async def disconnect(self, code: str) -> NoReturn:
        ...

    async def connect(self) -> NoReturn:
        await self.accept()


class Consumer(
    AbstractConsumer,
    # mixins.GroupNameMixin,
    mixins.HandlersMixin,
    mixins.RedisConsumerMixin,

):
    """
    TODO: docstrings
    TODO: разбить интерфейс по другим интерфейсам. т.к это "класс бога"
    """

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
        await self.send_notification(
            msg_type='group_discard',
            group_name=self.group_name,

        )

    async def receive(self, text_data: str = None, bytes_data: bytes = None) -> NoReturn:
        data: dict = loads(s=text_data) | self.__dict__

        message_type: str = data.get('type')

        match message_type:
            case 'search':
                await self.search(data=data)
            case 'message':
                await self.send_message(data=data)

    async def join_group(self, target: str, seeker: str) -> NoReturn:
        self.group_name: str = str(hash((target.strip('specific.'))))
        print(self.group_name)

        for channel_name in (target, seeker):
            await self.channel_layer.group_add(
                group=self.group_name,
                channel=channel_name,

            )

        await self.send_notification(
            msg_type='group_joined',
            group_name=self.group_name,
        )

    async def search(self, data: dict) -> None:
        channel_names = await self.redis.lrange(name=self.Meta.KEY, start=0, end=0)
        companion_channel_name = (channel_names[0].decode('UTF-8') if channel_names else None)
        user_channel_name = data.get('channel_name')  # channel name of the user who is connecting

        if companion_channel_name:
            return await self.join_group(
                target=companion_channel_name,
                seeker=user_channel_name,

            )

        await self.redis.rpush(self.Meta.KEY, user_channel_name)

    async def send_message(self, data: dict) -> NoReturn:
        await self.channel_layer.group_send(
            group=self.group_name,
            message=dict(
                type='message',
                message=data.get('message'),

            )
        )

    async def send_notification(self, msg_type: str, group_name: str) -> NoReturn:
        await self.channel_layer.group_send(
            group=group_name,
            message=dict(
                type=msg_type,

            )
        )

    async def message(self, event) -> NoReturn:
        await self.send(
            text_data=dumps(
                dict(
                    message=event['message'],

                )
            )
        )

    @clear_queues
    async def group_discard(self, _) -> NoReturn:
        await self.send(
            text_data=dumps(
                dict(
                    type='group.discard'
                ),
            )
        )

    @clear_queues
    async def group_joined(self, _) -> NoReturn:
        print('group joined')
        await self.send(
            text_data=dumps(
                dict(
                    type='group.joined'
                ),
            )
        )
