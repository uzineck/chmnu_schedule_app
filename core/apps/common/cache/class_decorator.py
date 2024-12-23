from dataclasses import dataclass
from functools import wraps
from typing import (
    Callable,
    ParamSpec,
    TypeVar,
)

from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout


F_Param = ParamSpec('F_Param')
F_Return = TypeVar('F_Return')


@dataclass(eq=False)
class BaseCacheDecorator:
    cache_service: BaseCacheService
    model_prefix: str
    identifier: str | bool | None = None
    func_prefix: str | None = None
    filters: str | None = None
    pagination_in: str | None = None

    def _manage_args_kwargs(self, *args, **kwargs):
        print(f'kwargs: {kwargs}')
        if self.identifier is True:
            if f"{self.model_prefix}_uuid" in kwargs:
                self.identifier = kwargs[f"{self.model_prefix}_uuid"]
            if "request" in args:
                self.identifier = args[0].auth

        if not self.filters and "filters" in kwargs:
            self.filters = kwargs["filters"]

        if not self.pagination_in and "pagination_in" in kwargs:
            self.pagination_in = kwargs["pagination_in"]


@dataclass
class BaseSetCacheDecorator(BaseCacheDecorator):
    timeout: Timeout | None = None

    def __call__(self, original_func: Callable[F_Param, F_Return]) -> F_Return:
        @wraps(original_func)
        def wrapped(*args: F_Param.args, **kwargs: F_Param.kwargs) -> F_Return:
            print(
                f'BaseSetCacheDecorator call values '
                f'{self.model_prefix=} '
                f'{self.timeout=} '
                f'{self.identifier=} '
                f'{self.func_prefix=} '
                f'{self.filters=} '
                f'{self.pagination_in=} ',
            )
            self._manage_args_kwargs(*args, **kwargs)
            print(
                f'BaseSetCacheDecorator after _manage_args_kwargs values '
                f'{self.model_prefix=} '
                f'{self.timeout=} '
                f'{self.identifier=} '
                f'{self.func_prefix=} '
                f'{self.filters=} '
                f'{self.pagination_in=} ',
            )
            cache_key = self.cache_service.generate_cache_key(
                model_prefix=self.model_prefix,
                identifier=self.identifier,
                func_prefix=self.func_prefix,
                filters=self.filters,
                pagination_in=self.pagination_in,
            )
            print(f'cache_key: {cache_key}')
            result = self.cache_service.get_cache_value(key=cache_key)
            if not result:
                result = original_func(*args, **kwargs)
                self.cache_service.set_cache(key=cache_key, value=result, timeout=self.timeout)
            return result
        return wrapped


class BaseDeleteCacheDecorator(BaseCacheDecorator):
    def __call__(self, original_func: Callable[F_Param, F_Return]) -> F_Return:
        @wraps(original_func)
        def wrapped(*args: F_Param.args, **kwargs: F_Param.kwargs) -> F_Return:
            print(
                f'BaseDeleteCacheDecorator call values '
                f'{self.model_prefix=} '
                f'{self.identifier=} '
                f'{self.func_prefix=} '
                f'{self.filters=} '
                f'{self.pagination_in=} ',
            )
            result = original_func(*args, **kwargs)
            self._manage_args_kwargs(**kwargs)
            print(
                f'BaseDeleteCacheDecorator after _manage_args_kwargs values '
                f'{self.model_prefix=} '
                f'{self.identifier=} '
                f'{self.func_prefix=} '
                f'{self.filters=} '
                f'{self.pagination_in=} ',
            )
            cache_key = self.cache_service.generate_cache_key(
                model_prefix=self.model_prefix,
                identifier=self.identifier,
                func_prefix=self.func_prefix,
                filters=self.filters,
                pagination_in=self.pagination_in,
            )
            print(f'cache_key: {cache_key}')

            self.cache_service.invalidate_cache_pattern(key=cache_key)
            return result
        return wrapped


@dataclass(eq=False)
class CacheDecorator:
    cache_service: BaseCacheService

    def get_or_set_cache(
            self,
            model_prefix: str,
            *,
            timeout: Timeout,
            identifier: str | bool | None = None,
            func_prefix: str | None = None,
            filters: str | None = None,
            pagination_in: str | None = None,
    ) -> F_Return:
        print('-' * 100)
        print(
            f'CacheDecorator values '
            f'{model_prefix=} {timeout=} {identifier=} {func_prefix=} {filters=} {pagination_in=} ',
        )
        return BaseSetCacheDecorator(
            model_prefix=model_prefix,
            timeout=timeout,
            identifier=identifier,
            func_prefix=func_prefix,
            filters=filters,
            pagination_in=pagination_in,
            cache_service=self.cache_service,
        )

    def delete_cache(
            self,
            model_prefix: str,
            *,
            identifier: str | bool | None = None,
            func_prefix: str | None = None,
            filters: str | None = None,
            pagination_in: str | None = None,
    ) -> F_Return:
        print('-' * 100)
        print(f'CacheDecorator values {model_prefix=} {identifier=} {func_prefix=} {filters=} {pagination_in=} ')
        return BaseDeleteCacheDecorator(
            model_prefix=model_prefix,
            identifier=identifier,
            func_prefix=func_prefix,
            filters=filters,
            pagination_in=pagination_in,
            cache_service=self.cache_service,
        )
