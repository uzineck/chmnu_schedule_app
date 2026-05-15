from core.apps.common.cache.class_decorator import CacheDecorator
from core.apps.common.cache.service import RedisCacheService


cache_decorator: CacheDecorator = CacheDecorator(cache_service=RedisCacheService())
