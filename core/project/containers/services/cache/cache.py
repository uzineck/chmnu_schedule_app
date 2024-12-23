import punq

from core.apps.common.cache.class_decorator import CacheDecorator
from core.apps.common.cache.service import (
    BaseCacheService,
    RedisCacheService,
)


def register_cache_services(container: punq.Container):
    container.register(BaseCacheService, RedisCacheService)
    container.register(CacheDecorator)
