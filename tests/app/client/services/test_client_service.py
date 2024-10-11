import pytest
from tests.fixtures.client.client import ClientModelFactory

from core.apps.clients.exceptions.auth import InvalidAuthDataException
from core.apps.clients.exceptions.client import (
    ClientAlreadyExistsException,
    ClientEmailNotFoundException,
    ClientRoleNotMatchingWithRequired,
)
from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole


@pytest.mark.django_db
def test_create_client_success(client_service: BaseClientService, generate_password):
    plain_password = generate_password()
    client = ClientModelFactory.build(password=plain_password)
    created_client = client_service.create(
        first_name=client.first_name,
        last_name=client.last_name,
        middle_name=client.middle_name,
        role=client.role,
        email=client.email,
        hashed_password=client.password,
    )

    assert created_client.first_name == client.first_name
    assert created_client.last_name == client.last_name
    assert created_client.middle_name == client.middle_name
    assert created_client.role == client.role
    assert created_client.email == client.email
    assert created_client.password == client.password


@pytest.mark.django_db
def test_create_client_already_exists_failure(client_service: BaseClientService):
    client = ClientModelFactory.create()
    with pytest.raises(ClientAlreadyExistsException):
        client_service.create(
            first_name=client.first_name,
            last_name=client.last_name,
            middle_name=client.middle_name,
            role=client.role,
            email=client.email,
            hashed_password=client.password,
        )


@pytest.mark.django_db
def test_get_client_success(client_service: BaseClientService):
    client = ClientModelFactory.create()
    found_client = client_service.get_by_email(
        email=client.email,
    )
    assert found_client.email == client.email


@pytest.mark.django_db
def test_get_client_not_found_failure(client_service: BaseClientService):
    client = ClientModelFactory.create()
    with pytest.raises(ClientEmailNotFoundException):
        client_service.get_by_email(email=f'wrong{client.email}')


@pytest.mark.django_db
def test_client_verification_success(client_service: BaseClientService, hash_password, generate_password):
    plain_password = generate_password()
    hashed_password = hash_password(plain_password=plain_password)
    client = ClientModelFactory.create(password=hashed_password)

    verified_client = client_service.validate_client(email=client.email, password=plain_password)

    assert verified_client.email == client.email
    assert verified_client.password == client.password


@pytest.mark.django_db
def test_client_verification_password_invalid_auth_failure(
        client_service: BaseClientService,
        hash_password,
        generate_password,
):
    plain_password = generate_password()
    new_plain_password = generate_password()
    hashed_password = hash_password(plain_password=plain_password)
    client = ClientModelFactory.create(password=hashed_password)
    with pytest.raises(InvalidAuthDataException):
        client_service.validate_client(email=client.email, password=new_plain_password)


@pytest.mark.django_db
def test_client_verification_email_invalid_auth_failure(
        client_service: BaseClientService,
        hash_password,
        generate_password,
):
    plain_password = generate_password()
    hashed_password = hash_password(plain_password=plain_password)
    client = ClientModelFactory.create(password=hashed_password)
    with pytest.raises(InvalidAuthDataException):
        client_service.validate_client(email=f'wrong{client.email}', password=plain_password)


@pytest.mark.django_db
def test_client_role_check_success(client_service: BaseClientService):
    client_headman = ClientModelFactory.build(role=ClientRole.HEADMAN)
    client_admin = ClientModelFactory.build(role=ClientRole.ADMIN)
    client_manager = ClientModelFactory.build(role=ClientRole.MANAGER)
    client_default = ClientModelFactory.build(role=ClientRole.DEFAULT)

    assert client_service.check_client_role(client_role=client_headman.role, required_role=ClientRole.HEADMAN) is None
    assert client_service.check_client_role(client_role=client_admin.role, required_role=ClientRole.ADMIN) is None
    assert client_service.check_client_role(client_role=client_manager.role, required_role=ClientRole.MANAGER) is None
    assert client_service.check_client_role(client_role=client_default.role, required_role=ClientRole.DEFAULT) is None


@pytest.mark.django_db
def test_client_role_check_failure(client_service: BaseClientService):
    client_headman = ClientModelFactory.build(role=ClientRole.HEADMAN)
    client_admin = ClientModelFactory.build(role=ClientRole.ADMIN)
    client_manager = ClientModelFactory.build(role=ClientRole.MANAGER)
    client_default = ClientModelFactory.build(role=ClientRole.DEFAULT)

    with pytest.raises(ClientRoleNotMatchingWithRequired):
        client_service.check_client_role(client_role=client_headman.role, required_role=ClientRole.ADMIN)

    with pytest.raises(ClientRoleNotMatchingWithRequired):
        client_service.check_client_role(client_role=client_admin.role, required_role=ClientRole.HEADMAN)

    with pytest.raises(ClientRoleNotMatchingWithRequired):
        client_service.check_client_role(client_role=client_manager.role, required_role=ClientRole.ADMIN)

    with pytest.raises(ClientRoleNotMatchingWithRequired):
        client_service.check_client_role(client_role=client_default.role, required_role=ClientRole.HEADMAN)


@pytest.mark.django_db
def test_client_update_email_success(client_service: BaseClientService, generate_email):
    client = ClientModelFactory.create()
    new_email = generate_email()
    updated_client = client_service.update_email(client=client, email=new_email)

    assert updated_client.email == new_email
    assert updated_client.email != client.email


@pytest.mark.django_db
def test_client_update_email_email_not_found_failure(client_service: BaseClientService, generate_email):
    client = ClientModelFactory.build()
    new_email = generate_email()

    with pytest.raises(ClientEmailNotFoundException):
        client_service.update_email(client=client, email=new_email)


@pytest.mark.django_db
def test_client_update_password_success(client_service: BaseClientService, hash_password, generate_password):
    client = ClientModelFactory.create()
    new_plain_password = generate_password()
    hashed_password = hash_password(plain_password=new_plain_password)
    updated_client = client_service.update_password(client=client, hashed_password=hashed_password)

    assert updated_client.password == hashed_password
    assert updated_client.password != client.password


@pytest.mark.django_db
def test_client_update_credentials_success(client_service: BaseClientService, faker_ua):
    client = ClientModelFactory.create()
    new_first_name = faker_ua.first_name()
    new_last_name = faker_ua.last_name()
    new_middle_name = faker_ua.last_name()

    updated_client = client_service.update_credentials(
        client=client,
        first_name=new_first_name,
        last_name=new_last_name,
        middle_name=new_middle_name,
    )

    assert updated_client.first_name == new_first_name, f'{new_first_name=}'
    assert updated_client.last_name == new_last_name, f'{new_last_name=}'
    assert updated_client.middle_name == new_middle_name, f'{new_middle_name=}'
