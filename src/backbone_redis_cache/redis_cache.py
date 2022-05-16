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
        self.__connection = connection
        self.__prefix = prefix
        self.__deserialize = deserializer
        self.__serialize = serializer

    async def get(self, key: str, default=None) -> Any:
        result: str = await self.__connection.get(self.__prefix + key)
        return self.__deserialize(result) if result is not None else default

    async def exists(self, key: str) -> bool:
        return await self.__connection.exists(self.__prefix + key) != 0

    async def set(self, key: str, value: Any, seconds: Optional[int] = None) -> None:
        await self.__connection.set(self.__prefix + key, self.__serialize(value), ex=seconds)

    async def mset(self, dictionary: Dict[str, Any], seconds: Optional[int] = None) -> None:
        pipe = self.__connection.pipeline()
        for key, value in dictionary.items():
            await pipe.set(self.__prefix + key, self.__serialize(value), ex=seconds)
        await pipe.execute()

    async def mget(self, keys: List[str], default=None) -> List[Any]:
        results = await self.__connection.mget([self.__prefix + key for key in keys])
        return [
            self.__deserialize(result) if result is not None else default
            for result in results
        ]

    async def forget(self, key) -> None:
        await self.__connection.delete(self.__prefix + key)

    async def flush(self):
        await self.__connection.flushdb()
        await self.__connection.flushall()