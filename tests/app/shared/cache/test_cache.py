import pytest
import redis.exceptions

from app.shared.cache import build_key, get_cache, set_cache


class TestCacheBuildKey:
    @staticmethod
    def test_cache_build_key_with_no_parts():
        key = build_key('cache')
        assert key == 'cache'

    @staticmethod
    def test_build_key_normalizes_with_none_in_parts():
        key = build_key('cache', ' By-Name ', ' name ', None)
        assert key == 'cache:by-name:name'

    @staticmethod
    def test_build_key_returns_prefix_when_parts_are_empty():
        key = build_key('cache', '', '   ')

        assert key == 'cache'

    @staticmethod
    def test_build_key_with_dict_part():
        key = build_key('cache', {'name': 'Thomas', 'order': 25})

        valid_keys = {
            'cache:name=thomas&order=25',
            'cache:order=25&name=thomas',
            'cache:name=Thomas&order=25',
            'cache:order=25&name=Thomas',
        }
        assert key in valid_keys

    @staticmethod
    def test_build_key_with_dict_none_in_part():
        key = build_key('cache', {'change': None})

        assert key == 'cache'


class TestCacheGetCache:
    @staticmethod
    @pytest.mark.asyncio
    async def test_set_and_get_cache(redis_client):
        key = build_key('cache', 'by-name', 'name')
        payload = {'name': 'name', 'order': 1}

        await set_cache(key, payload, ttl=10)
        result = await get_cache(key)

        assert result == payload

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_cache_returns_none_for_missing_key(redis_client):
        key = build_key('name', 'not-exist')

        result = await get_cache(key)

        assert result is None


class TestCacheSetCache:
    @staticmethod
    @pytest.mark.asyncio
    async def test_set_cache_with_zero_ttl(redis_client):
        key = build_key('name', 'meta')

        with pytest.raises(redis.exceptions.ResponseError):
            await set_cache(key, {'total': 1302}, ttl=0)

        result = await get_cache(key)

        assert result is None or result == {'total': 1302}
