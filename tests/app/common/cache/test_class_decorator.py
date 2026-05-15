from dataclasses import dataclass
from typing import Any

from core.apps.common.cache.class_decorator import CacheDecorator
from core.apps.common.cache.service import (
    BaseCacheService,
    CACHE_MISS,
)
from core.apps.common.cache.timeouts import Timeout


class InMemoryCacheService(BaseCacheService):
    """In-memory cache implementation for unit testing the decorator without
    Redis."""

    def __init__(self):
        self.store: dict[str, Any] = {}
        self.get_calls: list[str] = []
        self.set_calls: list[tuple[str, Any, int | None]] = []
        self.invalidate_calls: list[str] = []

    def generate_cache_key(self, model_prefix, *, identifier=None, func_prefix=None, filters=None, pagination_in=None):
        parts = [model_prefix]
        for part in (identifier, func_prefix, filters, pagination_in):
            if part is not None:
                parts.append(str(part))
        return '_'.join(parts)

    def get_cache_value(self, key, default=None):
        self.get_calls.append(key)
        return self.store.get(key, default)

    def set_cache(self, key, value, timeout=None):
        self.set_calls.append((key, value, timeout))
        self.store[key] = value

    def invalidate_cache(self, key):
        self.invalidate_calls.append(key)
        self.store.pop(key, None)

    def invalidate_cache_list(self, keys):
        for key in keys:
            self.invalidate_cache(key)

    def invalidate_cache_pattern(self, key):
        self.invalidate_calls.append(key)
        prefix = key.rstrip('*')
        for k in list(self.store.keys()):
            if k.startswith(prefix):
                self.store.pop(k, None)

    def invalidate_cache_pattern_list(self, keys):
        for key in keys:
            self.invalidate_cache_pattern(key)

    def try_acquire_lock(self, key, ttl):
        if key in self.store:
            return False
        self.store[key] = 1
        return True

    def release_lock(self, key):
        self.store.pop(key, None)


def test_get_or_set_caches_on_miss_returns_cached_on_hit():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)
    call_count = {'n': 0}

    @decorator.get_or_set_cache(model_prefix='thing', timeout=Timeout.HOUR)
    def compute():
        call_count['n'] += 1
        return 'result'

    assert compute() == 'result'
    assert compute() == 'result'

    assert call_count['n'] == 1
    assert len(cache_service.set_calls) == 1


def test_empty_list_is_valid_cached_value():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)
    call_count = {'n': 0}

    @decorator.get_or_set_cache(model_prefix='thing', timeout=Timeout.HOUR)
    def compute():
        call_count['n'] += 1
        return []

    assert compute() == []
    assert compute() == []

    assert call_count['n'] == 1


def test_none_is_valid_cached_value():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)
    call_count = {'n': 0}

    @decorator.get_or_set_cache(model_prefix='thing', timeout=Timeout.HOUR)
    def compute():
        call_count['n'] += 1
        return None

    assert compute() is None
    assert compute() is None

    assert call_count['n'] == 1


def test_decorator_stateless_across_different_kwargs():
    """Race-condition regression: the decorator must not mutate self between calls."""
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)

    @decorator.get_or_set_cache(
        model_prefix='group',
        identifier=lambda kw: kw['group_uuid'],
        func_prefix='lessons',
        timeout=Timeout.HOUR,
    )
    def get_lessons(group_uuid):
        return f'lessons-for-{group_uuid}'

    get_lessons(group_uuid='uuid-A')
    get_lessons(group_uuid='uuid-B')

    keys = [k for k, _, _ in cache_service.set_calls]
    assert 'group_uuid-A_lessons' in keys
    assert 'group_uuid-B_lessons' in keys
    assert len(cache_service.set_calls) == 2


def test_decorator_stateless_filters_per_call():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)

    @dataclass
    class Filter:
        value: str

    @decorator.get_or_set_cache(model_prefix='group', func_prefix='lessons', timeout=Timeout.HOUR)
    def get_lessons(filters):
        return f'lessons-{filters.value}'

    get_lessons(filters=Filter(value='a'))
    get_lessons(filters=Filter(value='b'))

    keys = [k for k, _, _ in cache_service.set_calls]
    assert len(set(keys)) == 2


def test_identifier_callable_resolves_from_kwargs():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)

    @decorator.get_or_set_cache(
        model_prefix='client',
        identifier=lambda kw: kw['email'],
        func_prefix='info',
        timeout=Timeout.HOUR,
    )
    def get_info(email):
        return 'data'

    get_info(email='user@example.com')

    keys = [k for k, _, _ in cache_service.set_calls]
    assert keys == ['client_user@example.com_info']


def test_delete_decorator_invalidates_after_call():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)
    cache_service.store['group_abc_lessons_a'] = 'cached'

    @decorator.delete_cache(model_prefix='group', identifier='abc', func_prefix='lessons')
    def write():
        return 'written'

    result = write()

    assert result == 'written'
    assert cache_service.invalidate_calls == ['group_abc_lessons']
    assert 'group_abc_lessons_a' not in cache_service.store


def test_delete_caches_resolves_callable_identifier_from_kwargs():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)

    @decorator.delete_caches([
        dict(model_prefix='teacher', func_prefix='all'),
        dict(
            model_prefix='teacher',
            identifier=lambda kw: kw['teacher_uuid'],
            func_prefix='lessons',
            filters='*',
        ),
    ])
    def write(teacher_uuid):
        return 'written'

    write(teacher_uuid='uuid-abc')

    assert cache_service.invalidate_calls == [
        'teacher_all',
        'teacher_uuid-abc_lessons_*',
    ]


def test_delete_caches_invalidates_all_specs():
    cache_service = InMemoryCacheService()
    decorator = CacheDecorator(cache_service=cache_service)

    @decorator.delete_caches([
        dict(model_prefix='faculty', func_prefix='all'),
        dict(model_prefix='faculty', func_prefix='list', filters='*', pagination_in='*'),
        dict(model_prefix='group', func_prefix='*'),
    ])
    def write():
        return 'written'

    result = write()

    assert result == 'written'
    assert cache_service.invalidate_calls == [
        'faculty_all',
        'faculty_list_*_*',
        'group_*',
    ]


def test_cache_miss_sentinel_distinguishes_from_cached_none():
    cache_service = InMemoryCacheService()

    assert cache_service.get_cache_value('missing-key', default=CACHE_MISS) is CACHE_MISS

    cache_service.set_cache('cached-none', None)

    assert cache_service.get_cache_value('cached-none', default=CACHE_MISS) is None
