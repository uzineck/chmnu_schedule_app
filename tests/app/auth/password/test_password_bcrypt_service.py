from tests.app.auth.password.conftest import hash_password
from tests.fixtures.client.utils import generate_password

from core.apps.common.authentication.password import BasePasswordService


def test_verify_password_success(password_service: BasePasswordService):
    """Test for successfully verifying plain password and hashed password."""
    plain_password = generate_password()
    hashed_password = hash_password(password_service=password_service, plain_password=plain_password)

    assert password_service.verify_password(plain_password=plain_password, hashed_password=hashed_password) is True


def test_verify_password_fail(password_service: BasePasswordService):
    """Test for failed verifying plain password and hashed password."""
    plain_password = generate_password()
    another_plain_password = generate_password()
    hashed_password = hash_password(password_service=password_service, plain_password=plain_password)

    assert (
        password_service.verify_password(plain_password=another_plain_password, hashed_password=hashed_password) is
        False
    )
