import pytest
from faker import Faker

from core.apps.clients.services.client import (
    BaseClientService,
    ORMClientService,
)
from core.apps.common.authentication.password import BcryptPasswordService
from core.apps.common.authentication.token import JWTTokenService


faker = Faker()


@pytest.fixture
def client_service() -> BaseClientService:
    password_service = BcryptPasswordService()
    token_service = JWTTokenService()
    return ORMClientService(password_service=password_service, token_service=token_service)


def generate_email() -> str:
    return f'{faker.user_name()}@gmail.com'
