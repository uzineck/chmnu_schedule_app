import pytest

from core.apps.clients.services.client import BaseClientService


@pytest.fixture
def client_service(container) -> BaseClientService:
    return container.resolve(BaseClientService)
