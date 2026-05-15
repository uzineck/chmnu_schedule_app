from dataclasses import dataclass
from pydantic import BaseModel

from core.apps.common.cache.service import RedisCacheService


service = RedisCacheService()


def test_generate_key_model_prefix_only():
    key = service.generate_cache_key(model_prefix='group')

    assert key == 'group'


def test_generate_key_with_identifier():
    key = service.generate_cache_key(model_prefix='group', identifier='abc-123')

    assert key == 'group_abc-123'


def test_generate_key_full_parts():
    key = service.generate_cache_key(
        model_prefix='group',
        identifier='abc-123',
        func_prefix='lessons',
    )

    assert key == 'group_abc-123_lessons'


def test_generate_key_wildcard_preserved():
    key = service.generate_cache_key(
        model_prefix='group',
        identifier='*',
        func_prefix='lessons',
    )

    assert key == 'group_*_lessons'


def test_generate_key_pydantic_filter_stable():
    class Filter(BaseModel):
        is_even: bool
        subgroup: str | None = None

    key_a = service.generate_cache_key(model_prefix='group', filters=Filter(is_even=True, subgroup='A'))
    key_b = service.generate_cache_key(model_prefix='group', filters=Filter(subgroup='A', is_even=True))

    assert key_a == key_b


def test_generate_key_pydantic_filter_changes_with_value():
    class Filter(BaseModel):
        is_even: bool

    key_true = service.generate_cache_key(model_prefix='group', filters=Filter(is_even=True))
    key_false = service.generate_cache_key(model_prefix='group', filters=Filter(is_even=False))

    assert key_true != key_false


def test_generate_key_dataclass_filter_stable():
    @dataclass
    class Filter:
        is_even: bool
        subgroup: str | None = None

    key_a = service.generate_cache_key(model_prefix='group', filters=Filter(is_even=True, subgroup='A'))
    key_b = service.generate_cache_key(model_prefix='group', filters=Filter(is_even=True, subgroup='A'))

    assert key_a == key_b


def test_generate_key_none_parts_omitted():
    key = service.generate_cache_key(
        model_prefix='group',
        identifier=None,
        func_prefix='lessons',
        filters=None,
        pagination_in=None,
    )

    assert key == 'group_lessons'
