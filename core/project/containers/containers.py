import punq
from functools import lru_cache

from core.project.containers.services.client.client import register_client_services
from core.project.containers.services.schedule import register_schedule_services
from core.project.containers.validators import register_validators


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    # Validator containers
    register_validators(container=container)

    # Client containers
    register_client_services(container=container)

    # Schedule containers
    register_schedule_services(container=container)

    return container
