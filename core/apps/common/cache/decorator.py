from core.apps.common.cache.class_decorator import CacheDecorator
from core.project.containers.containers import get_container


container = get_container()
cache_decorator: CacheDecorator = container.resolve(CacheDecorator)
