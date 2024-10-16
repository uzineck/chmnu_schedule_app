import punq

from core.apps.common.cache.service import (
    BaseCacheService,
    RedisCacheService,
)


def register_cache_services(container: punq.Container):
    container.register(BaseCacheService, RedisCacheService)
