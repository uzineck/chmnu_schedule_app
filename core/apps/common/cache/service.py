from django.core.cache import cache

import json
import random
from abc import (
    ABC,
    abstractmethod,
)
from typing import Any


CACHE_TTL_JITTER_RATIO = 0.1


CACHE_MISS = object()


class BaseCacheService(ABC):
    @abstractmethod
    def generate_cache_key(
            self,
            model_prefix: str,
            *,
            identifier: str | None = None,
            func_prefix: str | None = None,
            filters: Any = None,
            pagination_in: Any = None,
    ) -> str:
        ...

    @abstractmethod
    def get_cache_value(self, key: str, default: Any = None) -> Any:
        ...

    @abstractmethod
    def set_cache(self, key: str, value, timeout: int | None = None) -> None:
        ...

    @abstractmethod
    def invalidate_cache(self, key: str) -> None:
        ...

    @abstractmethod
    def invalidate_cache_list(self, keys: list[str]) -> None:
        ...

    @abstractmethod
    def invalidate_cache_pattern(self, key: str) -> None:
        ...

    @abstractmethod
    def invalidate_cache_pattern_list(self, keys: list[str]) -> None:
        ...

    @abstractmethod
    def try_acquire_lock(self, key: str, ttl: int) -> bool:
        ...

    @abstractmethod
    def release_lock(self, key: str) -> None:
        ...


class RedisCacheService(BaseCacheService):
    def generate_cache_key(
            self,
            model_prefix: str,
            identifier: str | None = None,
            func_prefix: str | None = None,
            filters: Any = None,
            pagination_in: Any = None,
    ) -> str:
        parts = [model_prefix]
        if identifier is not None:
            parts.append(self._stringify_for_key(identifier))
        if func_prefix is not None:
            parts.append(self._stringify_for_key(func_prefix))
        if filters is not None:
            parts.append(self._stringify_for_key(filters))
        if pagination_in is not None:
            parts.append(self._stringify_for_key(pagination_in))
        return '_'.join(parts)

    @staticmethod
    def _stringify_for_key(value: Any) -> str:
        if isinstance(value, str):
            return value
        if hasattr(value, 'model_dump'):
            return json.dumps(value.model_dump(), sort_keys=True, default=str)
        if hasattr(value, '__dict__'):
            return json.dumps(vars(value), sort_keys=True, default=str)
        return str(value)

    def get_cache_value(self, key: str, default: Any = None) -> Any:
        return cache.get(key=key, default=default)

    def set_cache(
            self,
            key: str,
            value,
            timeout: int | None = None,
    ) -> None:
        if timeout is not None:
            jitter = random.uniform(-CACHE_TTL_JITTER_RATIO, CACHE_TTL_JITTER_RATIO) * timeout  # noqa: DUO102
            timeout = max(1, int(timeout + jitter))
        cache.set(key=key, value=value, timeout=timeout)

    def invalidate_cache(self, key: str) -> None:
        cache.delete(key=key)

    def invalidate_cache_list(self, keys: list[str]) -> None:
        for key in keys:
            cache.delete(key=key)

    def invalidate_cache_pattern(self, key: str) -> None:
        cache.delete_pattern(key)

    def invalidate_cache_pattern_list(self, keys: list[str]) -> None:
        for key in keys:
            cache.delete_pattern(key)

    def try_acquire_lock(self, key: str, ttl: int) -> bool:
        return cache.add(key, 1, timeout=ttl)

    def release_lock(self, key: str) -> None:
        cache.delete(key)
