import pytest

from core.apps.clients.services.client import BaseClientService
from core.apps.common.authentication.password import BasePasswordService


@pytest.fixture
def client_service(container) -> BaseClientService:
    return container.resolve(BaseClientService)


@pytest.fixture
def password_service(container) -> BasePasswordService:
    return container.resolve(BasePasswordService)


@pytest.fixture
def hash_password(password_service: BasePasswordService):
    def _hash_password(plain_password: str) -> str:
        return password_service.hash_password(plain_password)

    return _hash_password


@pytest.fixture
def generate_email(faker):
    def _generate_email() -> str:
        return f'{faker.user_name()}@gmail.com'

    return _generate_email


@pytest.fixture
def generate_password(faker):
    def _generate_password() -> str:
        return faker.password(length=10)

    return _generate_password
