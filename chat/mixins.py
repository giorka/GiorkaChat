from json import dumps
from typing import NoReturn, Optional

from redis import asyncio as aioredis


# def clear_queues(function: callable) -> callable:
    # async def wrapper(*args, **kwargs) -> NoReturn:
    #     await RedisConsumerMixin.redis.delete(RedisConsumerMixin.Meta.KEY)
    #     return await function(*args, **kwargs)
    #
    # return wrapper


# class RedisConsumerMixin:
#     redis = aioredis.Redis()
#
#     class Meta:
#         KEY = 'queue'


# class GroupNameMixin:
#     channel_name = None
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)
#         self.__group_name: Optional[str] = None
#
#     @property
#     def group_name(self) -> str:
#         if not self.__group_name:
#             self.__group_name = str(hash((self.channel_name.strip('specific.'))))
#
#         return self.__group_name
#
#     @group_name.setter
#     def group_name(self, value: str) -> NoReturn:
#         self.__group_name: str = value


# class HandlersMixin:
    # async def send(self, *args, **kwargs):
    #     ...

    # @clear_queues
    # async def group_discard(self, _) -> NoReturn:
    #     await self.send(
    #         text_data=dumps(
    #             dict(
    #                 type='group.discard'
    #             ),
    #         )
    #     )
    #
    # @clear_queues
    # async def group_joined(self, _) -> NoReturn:
    #     await self.send(
    #         text_data=dumps(
    #             dict(
    #                 type='group.joined'
    #             ),
    #         )
    #     )
