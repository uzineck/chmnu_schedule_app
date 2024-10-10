import pytest

from core.apps.common.authentication.password import BasePasswordService


@pytest.fixture
def password_service(container) -> BasePasswordService:
    return container.resolve(BasePasswordService)


def hash_password(password_service: BasePasswordService, plain_password: str) -> str:
    return password_service.hash_password(plain_password=plain_password)
