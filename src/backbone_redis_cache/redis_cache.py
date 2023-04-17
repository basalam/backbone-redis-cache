import json
from typing import Dict, Any, Optional, List, Callable
import aioredis


class RedisCache:
    def __init__(
            self,
            connection : aioredis.Redis,
            prefix: str = "",
            serializer : Optional[Callable] = json.dumps,
            deserializer : Optional[Callable] = json.loads,
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
        number = await self.__connection.incrby(self.__prefix + key, increment)
        if number == increment:
            await self.__connection.pexpire(self.__prefix + key, seconds * 1000)

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
        number = await self.__connection.get(self.__prefix + key)
        return 0 if number is None else int(number)

    async def forget(self, key) -> None:
        await self._connection.delete(self._prefix + key)

    async def flush(self):
        await self._connection.flushdb()
        await self._connection.flushall()