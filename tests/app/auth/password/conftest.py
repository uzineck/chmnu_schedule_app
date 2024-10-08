import pytest
from faker import Faker

from core.apps.common.authentication.password import (
    BasePasswordService,
    BcryptPasswordService,
)


faker = Faker()


@pytest.fixture
def password_service() -> BasePasswordService:
    return BcryptPasswordService()


def generate_password() -> str:
    return faker.password()


def hash_password(password_service: BasePasswordService, plain_password: str) -> str:
    return password_service.hash_password(plain_password=plain_password)
