#### Requirements

- Python 3.6+

#### Installation & Upgrade

```shell
pip install backbone-redis-cache
```

#### Usage

```python
from basalam.backbone_redis_cache import RedisCache
from redis.asyncio import Redis


cache = RedisCache(
    connection=Redis(host="127.0.0.1", port=6379),
    prefix="ORDER_CACHE."
)

await cache.set("key", "value", seconds=10 * 60)
await cache.get("key", default="Nevermind")

await cache.mset({'key1': "value1",'key2': "value2"}, seconds=15 * 60)
await cache.mget(["key1", "key2"], default="Whatever")

# Counter Manipulation
await cache.cset("key", 1, seconds=60)
await cache.cget("key")

await cache.exists("key")
await cache.forget("key")

await cache.flush()
```

#### Testing

```bash
# install pytest
pip install pytest

# run tests
python -m pytest
```

#### Changelog
- 0.0.3 Now build and push are done using gitlab-ci
- 0.0.5 set & get a counter thanks to abdi.zbn@gmail.com
- 0.0.10 added scan method thanks to ali.alimohammadi@basalam.com
