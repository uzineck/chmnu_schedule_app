import inspect
import logging
import time
from dataclasses import dataclass
from functools import wraps
from typing import (
    Any,
    Callable,
    ParamSpec,
    TypeVar,
)

from core.apps.common.cache.service import (
    BaseCacheService,
    CACHE_MISS,
)
from core.apps.common.cache.timeouts import Timeout


logger = logging.getLogger(__name__)

F_Param = ParamSpec('F_Param')
F_Return = TypeVar('F_Return')

LOCK_TTL_SECONDS = 10
FOLLOWER_POLL_INTERVAL = 0.05
FOLLOWER_MAX_POLLS = 20


def _resolve_identifier(identifier: Any, kwargs: dict, result: Any) -> Any:
    """Resolve identifier; callables may take (kwargs) or (kwargs, result)."""
    if not callable(identifier):
        return identifier
    arity = len(inspect.signature(identifier).parameters)
    if arity == 1:
        return identifier(kwargs)
    return identifier(kwargs, result)


@dataclass(eq=False, frozen=True)
class BaseCacheDecorator:
    cache_service: BaseCacheService
    model_prefix: str
    identifier: str | Callable | None = None
    func_prefix: str | None = None
    filters: Any = None
    pagination_in: Any = None

    def _resolve_key_params(self, args: tuple, kwargs: dict, result: Any = None) -> dict[str, Any]:
        """Compute per-call cache key params WITHOUT mutating self."""
        identifier = _resolve_identifier(self.identifier, kwargs, result)

        filters = self.filters if self.filters is not None else kwargs.get('filters')
        pagination = self.pagination_in if self.pagination_in is not None else kwargs.get('pagination_in')

        return {
            'model_prefix': self.model_prefix,
            'identifier': identifier,
            'func_prefix': self.func_prefix,
            'filters': filters,
            'pagination_in': pagination,
        }


@dataclass(eq=False, frozen=True)
class BaseSetCacheDecorator(BaseCacheDecorator):
    timeout: Timeout | None = None

    def __call__(self, original_func: Callable[F_Param, F_Return]) -> Callable[F_Param, F_Return]:
        @wraps(original_func)
        def wrapped(*args: F_Param.args, **kwargs: F_Param.kwargs) -> F_Return:
            params = self._resolve_key_params(args, kwargs)
            cache_key = self.cache_service.generate_cache_key(**params)

            cached = self.cache_service.get_cache_value(key=cache_key, default=CACHE_MISS)
            if cached is not CACHE_MISS:
                logger.debug('cache hit: %s', cache_key)
                return cached

            lock_key = f'{cache_key}:lock'
            if self.cache_service.try_acquire_lock(lock_key, ttl=LOCK_TTL_SECONDS):
                logger.debug('cache miss (leader): %s', cache_key)
                try:
                    result = original_func(*args, **kwargs)
                    self.cache_service.set_cache(key=cache_key, value=result, timeout=self.timeout)
                    return result
                finally:
                    self.cache_service.release_lock(lock_key)

            logger.debug('cache miss (follower, waiting): %s', cache_key)
            for _ in range(FOLLOWER_MAX_POLLS):
                time.sleep(FOLLOWER_POLL_INTERVAL)
                cached = self.cache_service.get_cache_value(key=cache_key, default=CACHE_MISS)
                if cached is not CACHE_MISS:
                    return cached

            logger.debug('cache miss (follower, fallback): %s', cache_key)
            return original_func(*args, **kwargs)

        return wrapped


@dataclass(eq=False, frozen=True)
class BaseDeleteCacheDecorator(BaseCacheDecorator):
    def __call__(self, original_func: Callable[F_Param, F_Return]) -> Callable[F_Param, F_Return]:
        @wraps(original_func)
        def wrapped(*args: F_Param.args, **kwargs: F_Param.kwargs) -> F_Return:
            result = original_func(*args, **kwargs)
            params = self._resolve_key_params(args, kwargs, result)
            cache_key = self.cache_service.generate_cache_key(**params)
            logger.debug('cache invalidate (pattern): %s', cache_key)
            self.cache_service.invalidate_cache_pattern(key=cache_key)
            return result

        return wrapped


@dataclass(eq=False, frozen=True)
class BaseDeleteManyCacheDecorator:
    cache_service: BaseCacheService
    key_specs: tuple[dict, ...]

    @staticmethod
    def _resolve_spec(spec: dict, args: tuple, kwargs: dict, result: Any = None) -> dict:
        identifier = spec.get('identifier')
        if not callable(identifier):
            return spec
        resolved = dict(spec)
        resolved['identifier'] = _resolve_identifier(identifier, kwargs, result)
        return resolved

    def __call__(self, original_func: Callable[F_Param, F_Return]) -> Callable[F_Param, F_Return]:
        @wraps(original_func)
        def wrapped(*args: F_Param.args, **kwargs: F_Param.kwargs) -> F_Return:
            result = original_func(*args, **kwargs)
            keys = [
                self.cache_service.generate_cache_key(**self._resolve_spec(spec, args, kwargs, result))
                for spec in self.key_specs
            ]
            logger.debug('cache invalidate (patterns): %s', keys)
            self.cache_service.invalidate_cache_pattern_list(keys=keys)
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
            identifier: str | Callable | None = None,
            func_prefix: str | None = None,
            filters: Any = None,
            pagination_in: Any = None,
    ) -> BaseSetCacheDecorator:
        return BaseSetCacheDecorator(
            cache_service=self.cache_service,
            model_prefix=model_prefix,
            identifier=identifier,
            func_prefix=func_prefix,
            filters=filters,
            pagination_in=pagination_in,
            timeout=timeout,
        )

    def delete_cache(
            self,
            model_prefix: str,
            *,
            identifier: str | Callable | None = None,
            func_prefix: str | None = None,
            filters: Any = None,
            pagination_in: Any = None,
    ) -> BaseDeleteCacheDecorator:
        return BaseDeleteCacheDecorator(
            cache_service=self.cache_service,
            model_prefix=model_prefix,
            identifier=identifier,
            func_prefix=func_prefix,
            filters=filters,
            pagination_in=pagination_in,
        )

    def delete_caches(self, key_specs: list[dict]) -> BaseDeleteManyCacheDecorator:
        return BaseDeleteManyCacheDecorator(
            cache_service=self.cache_service,
            key_specs=tuple(dict(spec) for spec in key_specs),
        )
