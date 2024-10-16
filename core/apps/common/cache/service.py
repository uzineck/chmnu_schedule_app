from django.core.cache import cache

from abc import (
    ABC,
    abstractmethod,
)
from typing import Any


class BaseCacheService(ABC):
    @abstractmethod
    def get_cache_key(
            self,
            model_prefix: str,
            identifier: str | None = None,
            func_prefix: str | None = None,
            filters: str | None = None,
            pagination_in: str | None = None,
    ) -> str:
        ...

    @abstractmethod
    def get_cache_value(self, key: str) -> Any:
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


class RedisCacheService(BaseCacheService):
    def get_cache_key(
            self,
            model_prefix: str,
            identifier: str | None = None,
            func_prefix: str | None = None,
            filters: str | None = None,
            pagination_in: str | None = None,
    ) -> str:
        return (
            f"{model_prefix}"
            f"{f'_{identifier}' if identifier else ''}"
            f"{f'_{func_prefix}' if func_prefix else ''}"
            f"{f'_{filters}' if filters else ''}"
            f"{f'_{pagination_in}' if pagination_in else ''}"
        )

    def get_cache_value(self, key: str) -> Any:
        return cache.get(key=key)

    def set_cache(
            self,
            key: str,
            value,
            timeout: int | None = None,
    ) -> None:
        cache.set(key=key, value=value, timeout=timeout)

    def invalidate_cache(self, key: str) -> None:
        cache.delete(key=key)

    def invalidate_cache_list(self, keys: list[str]) -> None:
        for key in keys:
            cache.delete(key=key)

    def invalidate_cache_pattern(self, key: str) -> None:
        cache.delete_pattern(f'{key}*')

    def invalidate_cache_pattern_list(self, keys: list[str]) -> None:
        for key in keys:
            cache.delete_pattern(f'{key}*')
