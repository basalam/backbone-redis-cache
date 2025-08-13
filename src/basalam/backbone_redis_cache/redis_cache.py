import json
from typing import Dict, Any, Optional, List, Callable

try:
    from aioredis import Redis
except Exception as ex:
    from redis.asyncio import Redis


class RedisCache:
    __callbacks: List[Callable[[str, Any], None]] = []

    def __init__(
            self,
            connection: Redis,
            prefix: str = "",
            serializer: Optional[Callable] = json.dumps,
            deserializer: Optional[Callable] = json.loads,
    ) -> None:
        self._connection = connection
        self._prefix = prefix
        self._deserialize = deserializer
        self._serialize = serializer

    @classmethod
    def add_callback(cls, callback: Callable[[str, Any], None]) -> None:
        cls.__callbacks.append(callback)

    @classmethod
    def clear_callbacks(cls) -> None:
        cls.__callbacks.clear()

    def _trigger(self, operation: str, details: Any = None) -> None:
        for callback in self.__callbacks:
            callback(operation, details)

    async def get(self, key: str, default=None) -> Any:
        self._trigger("GET", key)
        result: str = await self._connection.get(self._prefix + key)
        return self._deserialize(result) if result is not None else default

    async def exists(self, key: str) -> bool:
        self._trigger("EXISTS", key)
        return await self._connection.exists(self._prefix + key) != 0

    async def set(self, key: str, value: Any, seconds: Optional[int] = None) -> None:
        self._trigger("SET", key)
        await self._connection.set(self._prefix + key, self._serialize(value), ex=seconds)

    async def cset(self, key: str, increment: int = 1, seconds: Optional[int] = None) -> None:
        self._trigger("CSET", key)
        number = await self._connection.incrby(self._prefix + key, increment)
        if number == increment:
            await self._connection.pexpire(self._prefix + key, seconds * 1000)

    async def mset(self, dictionary: Dict[str, Any], seconds: Optional[int] = None) -> None:
        self._trigger("MSET", list(dictionary.keys()))
        pipe = self._connection.pipeline()
        for key, value in dictionary.items():
            await pipe.set(self._prefix + key, self._serialize(value), ex=seconds)
        await pipe.execute()

    async def mget(self, keys: List[str], default=None) -> List[Any]:
        self._trigger("MGET", keys)
        results = await self._connection.mget([self._prefix + key for key in keys])
        return [
            self._deserialize(result) if result is not None else default
            for result in results
        ]

    async def cget(self, key: str) -> int:
        self._trigger("CGET", key)
        number = await self._connection.get(self._prefix + key)
        return 0 if number is None else int(number)

    async def forget(self, key) -> None:
        self._trigger("FORGET", key)
        await self._connection.delete(self._prefix + key)

    async def flush(self):
        self._trigger("FLUSH", None)
        await self._connection.flushdb()
        await self._connection.flushall()

    async def hset(self, name, key, value):
        self._trigger("HSET", {"name": name, "field": key})
        await self._connection.hset(name=self._prefix + name, key=key, value=value)

    async def hget(self, name, key):
        self._trigger("HGET", {"name": name, "field": key})
        return await self._connection.hget(name=self._prefix + name, key=key)

    async def expire(self, name, _time):
        self._trigger("EXPIRE", name)
        await self._connection.expire(name=self._prefix + name, time=_time)

    async def scan(self, match: Optional[str] = "*") -> List:
        self._trigger("SCAN", match)
        return_ = []
        cursor = '0'
        while cursor:
            cursor, keys = await self._connection.scan(cursor=cursor, match=self._prefix + match)
            return_.extend(keys)
            if cursor == b'0':
                break
        return return_

    async def unlink(self, keys: List[str]) -> None:
        prefixed_keys = [self._prefix + key for key in keys]
        self._trigger("UNLINK", prefixed_keys)
        await self._connection.unlink(*prefixed_keys)