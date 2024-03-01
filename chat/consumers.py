from json import loads
from typing import NoReturn

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from redis import Redis


class ConsumerMixin:
    async def accept(self):
        ...

    async def connect(self) -> NoReturn:
        await self.accept()


class Consumer(AsyncWebsocketConsumer, ConsumerMixin):
    """
    TODO: определить метод для поиска
    """

    redis = Redis(db=2)
    channel_layer = get_channel_layer()

    class Meta:
        KEY = 'query'
        CLEAR_TIME = 43200  # NOTE: in seconds

    @classmethod
    def remove(cls, value: str) -> NoReturn:
        cls.redis.lrem(name=cls.Meta.KEY, count=1, value=value)

    async def disconnect(self, code) -> NoReturn:
        """
        TODO: отправить письмо собеседнику (если есть), что пользователь покинул чат
        """

        self.remove(value=self.channel_name)

    async def receive(self, text_data=None, bytes_data=None) -> NoReturn:
        data = loads(s=text_data) | self.__dict__

        message_type = data.get('type')

        match message_type:
            case 'search':
                await self.search(data=data)
            # case '':
            #     ...

    @classmethod
    async def join_group(cls, target: str, seeker: str) -> NoReturn:
        group_name = str(hash((target.strip('specific.') + seeker.strip('specific.'))))

        for channel_name in (target, seeker):
            await cls.channel_layer.group_add(
                group=group_name,
                channel=channel_name,

            )

        cls.remove(value=target)

    @classmethod
    def search(cls, data: dict) -> NoReturn:
        channel_names = cls.redis.lrange(name=cls.Meta.KEY, start=0, end=0)
        channel_name = (
            channel_names[0].decode('UTF-8') if channel_names else None
        )  # name of the channel the user we are connecting to

        user_channel_name = data.get('channel_name')  # channel name of the user who is connecting

        # TODO: refactor
        if channel_name:
            return cls.join_group(target=channel_name, seeker=user_channel_name)
        else:
            with cls.redis.pipeline() as pipeline:
                if cls.redis.ttl(cls.Meta.KEY) == -1:
                    pipeline.expire(cls.Meta.KEY, time=cls.Meta.CLEAR_TIME)

                pipeline.rpush(cls.Meta.KEY, user_channel_name)
                pipeline.execute()
