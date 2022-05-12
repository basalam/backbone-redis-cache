#### Requirements

- Python 3.6+

#### Installation & Upgrade

```shell
pip install backbone-redis-cache --extra-index-url https://repo.basalam.dev/artifactory/api/pypi/basalam-pypi-local/simple --upgrade
```

#### Usage

```python
from backbone.redis_cache.redis_cache import RedisCache
import aioredis

cache = RedisCache(
    connection=aioredis.Redis(host="127.0.0.1", port=6379),
    prefix="ORDER_CACHE."
)

await cache.set("key", "value", seconds=10 * 60)
await cache.get("key", default="Nevermind")

await cache.mset({'key1': "value1",'key2': "value2"}, seconds=15 * 60)
await cache.mget(["key1", "key2"], default="Whatever")

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

#### Development

```bash
# install requirements
pip install build twine

# Build package
make build

# Push to basalam repository
make push
```