import json
from typing import Dict, Any, Optional, List, Callable

try:
    from aioredis import Redis
except Exception as ex:
    from redis.asyncio import Redis


class RedisCache:
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

    async def get(self, key: str, default=None) -> Any:
        result: str = await self._connection.get(self._prefix + key)
        return self._deserialize(result) if result is not None else default

    async def exists(self, key: str) -> bool:
        return await self._connection.exists(self._prefix + key) != 0

    async def set(self, key: str, value: Any, seconds: Optional[int] = None) -> None:
        await self._connection.set(self._prefix + key, self._serialize(value), ex=seconds)

    async def cset(self, key: str, increment: int = 1, seconds: Optional[int] = None) -> None:
        number = await self._connection.incrby(self._prefix + key, increment)
        if number == increment:
            await self._connection.pexpire(self._prefix + key, seconds * 1000)

    async def mset(self, dictionary: Dict[str, Any], seconds: Optional[int] = None) -> None:
        pipe = self._connection.pipeline()
        for key, value in dictionary.items():
            await pipe.set(self._prefix + key, self._serialize(value), ex=seconds)
        await pipe.execute()

    async def mget(self, keys: List[str], default=None) -> List[Any]:
        results = await self._connection.mget([self._prefix + key for key in keys])
        return [
            self._deserialize(result) if result is not None else default
            for result in results
        ]

    async def cget(self, key: str) -> int:
        number = await self._connection.get(self._prefix + key)
        return 0 if number is None else int(number)

    async def forget(self, key) -> None:
        await self._connection.delete(self._prefix + key)

    async def flush(self):
        await self._connection.flushdb()
        await self._connection.flushall()

    async def hset(self, name, key, value):
        await self._connection.hset(name=self._prefix + name, key=key, value=value)

    async def hget(self, name, key):
        return await self._connection.hget(name=self._prefix + name, key=key)

    async def expire(self, name, _time):
        await self._connection.expire(name=self._prefix + name, time=_time)

    async def scan(self, match: Optional[str] = "*") -> List:
        return_ = []
        cursor = '0'
        while cursor:
            cursor, keys = await self._connection.scan(cursor=cursor, match=self._prefix + match)
            return_.extend(keys)
            if cursor == b'0':
                break
        return return_
