import pytest
from redis.exceptions import RedisError

from app.shared.cache import CacheService


class BrokenRedis:
    @staticmethod
    async def get(key):
        raise RedisError(f'unavailable: {key}')

    @staticmethod
    async def set(key, value, ex=None):
        raise RedisError(f'unavailable: {key}')

    @staticmethod
    async def delete(key):
        raise RedisError(f'unavailable: {key}')


class BrokenPipeline:
    async def __aenter__(self):
        raise RedisError('pipeline unavailable')

    async def __aexit__(self, exc_type, exc, tb):
        return False


class BrokenRedisWithPipeline(BrokenRedis):
    @staticmethod
    def pipeline(transaction=False):
        return BrokenPipeline()


@pytest.mark.asyncio
async def test_build_key_normalizes_parts(redis_client):
    cache_service = CacheService(prefix='pokemon')

    result = cache_service.build_key(' By-Name ', ' Pikachu ')

    assert result == 'pokemon:by-name:pikachu'


@pytest.mark.asyncio
async def test_build_key_returns_prefix_when_parts_are_empty(redis_client):
    cache_service = CacheService(prefix='pokemon')

    result = cache_service.build_key('', '   ')

    assert result == 'pokemon'


@pytest.mark.asyncio
async def test_set_json_and_get_json_roundtrip(redis_client):
    cache_service = CacheService(prefix='pokemon')
    key = cache_service.build_key('by-name', 'bulbasaur')
    payload = {'name': 'bulbasaur', 'order': 1}

    await cache_service.set_json(key=key, value=payload)
    result = await cache_service.get_json(key)

    assert result == payload


@pytest.mark.asyncio
async def test_set_json_without_expiration(redis_client):
    cache_service = CacheService(prefix='pokemon')
    key = cache_service.build_key('meta')

    await cache_service.set_json(key=key, value={'total': 1302}, ttl_seconds=0)

    assert await cache_service.get_json(key) == {'total': 1302}
    assert await redis_client.ttl(key) == -1


@pytest.mark.asyncio
async def test_set_many_json_stores_multiple_values(redis_client):
    cache_service = CacheService(prefix='pokemon')
    key_values = {
        cache_service.build_key('by-name', 'bulbasaur'): {'name': 'bulbasaur', 'order': 1},
        cache_service.build_key('by-name', 'ivysaur'): {'name': 'ivysaur', 'order': 2},
    }

    await cache_service.set_many_json(key_values=key_values)

    assert await cache_service.get_json(cache_service.build_key('by-name', 'bulbasaur')) == {
        'name': 'bulbasaur',
        'order': 1,
    }
    assert await cache_service.get_json(cache_service.build_key('by-name', 'ivysaur')) == {
        'name': 'ivysaur',
        'order': 2,
    }


@pytest.mark.asyncio
async def test_set_many_json_returns_early_when_key_values_is_empty(redis_client):
    cache_service = CacheService(prefix='pokemon')

    await cache_service.set_many_json(key_values={})

    assert await redis_client.dbsize() == 0


@pytest.mark.asyncio
async def test_set_many_json_without_expiration(redis_client):
    cache_service = CacheService(prefix='pokemon')
    key = cache_service.build_key('catalog')

    await cache_service.set_many_json(
        key_values={key: [{'name': 'bulbasaur'}]},
        ttl_seconds=0,
    )

    assert await cache_service.get_json(key) == [{'name': 'bulbasaur'}]
    assert await redis_client.ttl(key) == -1


@pytest.mark.asyncio
async def test_delete_removes_value(redis_client):
    cache_service = CacheService(prefix='pokemon')
    key = cache_service.build_key('catalog')

    await cache_service.set_json(key=key, value=[{'name': 'bulbasaur'}])
    await cache_service.delete(key)

    assert await cache_service.get_json(key) is None


@pytest.mark.asyncio
async def test_get_json_returns_none_when_redis_is_unavailable(redis_client):
    cache_service = CacheService(prefix='pokemon')
    cache_service.redis = BrokenRedis()

    result = await cache_service.get_json('pokemon:catalog')

    assert result is None


@pytest.mark.asyncio
async def test_set_json_does_not_raise_when_redis_is_unavailable(redis_client):
    cache_service = CacheService(prefix='pokemon')
    cache_service.redis = BrokenRedis()

    await cache_service.set_json(key='pokemon:catalog', value={'name': 'bulbasaur'})
    await cache_service.delete('pokemon:catalog')


@pytest.mark.asyncio
async def test_set_many_json_does_not_raise_when_pipeline_is_unavailable(redis_client):
    cache_service = CacheService(prefix='pokemon')
    cache_service.redis = BrokenRedisWithPipeline()

    await cache_service.set_many_json(
        key_values={'pokemon:catalog': [{'name': 'bulbasaur'}]},
    )
