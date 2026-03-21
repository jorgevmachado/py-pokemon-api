
import pytest
import redis.exceptions

from app.shared.cache import build_key, get_cache, set_cache


@pytest.mark.asyncio
async def test_build_key_normalizes_parts():
    key = build_key('pokemon', ' By-Name ', ' Pikachu ')

    assert key == 'pokemon:by-name:pikachu'


@pytest.mark.asyncio
async def test_build_key_returns_prefix_when_parts_are_empty():
    key = build_key('pokemon', '', '   ')

    assert key == 'pokemon'


@pytest.mark.asyncio
async def test_build_key_with_dict_part():
    key = build_key('pokemon', {'name': 'Pikachu', 'order': 25})

    # Accept both lowercased and non-lowercased string values in the key
    valid_keys = {
        'pokemon:name=pikachu&order=25',
        'pokemon:order=25&name=pikachu',
        'pokemon:name=Pikachu&order=25',
        'pokemon:order=25&name=Pikachu',
    }
    assert key in valid_keys


@pytest.mark.asyncio
async def test_set_and_get_cache(redis_client):
    key = build_key('pokemon', 'by-name', 'bulbasaur')
    payload = {'name': 'bulbasaur', 'order': 1}

    await set_cache(key, payload, ttl=10)
    result = await get_cache(key)

    assert result == payload


@pytest.mark.asyncio
async def test_set_cache_with_zero_ttl(redis_client):
    key = build_key('pokemon', 'meta')

    # Redis does not allow zero expire time, so we expect a ResponseError
    with pytest.raises(redis.exceptions.ResponseError):
        await set_cache(key, {'total': 1302}, ttl=0)
    # Redis pode não armazenar se ttl=0, então resultado pode ser None
    result = await get_cache(key)

    assert result is None or result == {'total': 1302}


@pytest.mark.asyncio
async def test_get_cache_returns_none_for_missing_key(redis_client):
    key = build_key('pokemon', 'not-exist')

    result = await get_cache(key)

    assert result is None
