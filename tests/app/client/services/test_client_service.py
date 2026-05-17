import pytest
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.exceptions.client import (
    ClientAlreadyExistsException,
    ClientNotFoundException,
    ClientUpdateException,
)
from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import ClientRole


@pytest.fixture
def create_client_with_password(client_create, generate_password, hash_password):
    plain_password = generate_password()
    hashed_password = hash_password(plain_password)
    client = client_create(password=hashed_password)
    return client, plain_password


@pytest.fixture
def build_client_with_password(client_build, generate_password, hash_password):
    plain_password = generate_password()
    hashed_password = hash_password(plain_password)
    client = client_build(password=hashed_password)
    return client, plain_password


@pytest.mark.django_db
def test_create_client_success(client_service: BaseClientService, build_client_with_password):
    client, plain_password = build_client_with_password
    created_client = client_service.create(
        first_name=client.first_name,
        last_name=client.last_name,
        middle_name=client.middle_name,
        email=client.email,
        hashed_password=client.password,
    )

    assert created_client.first_name == client.first_name
    assert created_client.last_name == client.last_name
    assert created_client.middle_name == client.middle_name
    assert created_client.email == client.email


@pytest.mark.django_db
def test_create_client_already_exists_failure(client_service: BaseClientService, client_create):
    client = client_create()
    with pytest.raises(ClientAlreadyExistsException):
        client_service.create(
            first_name=client.first_name,
            last_name=client.last_name,
            middle_name=client.middle_name,
            email=client.email,
            hashed_password=client.password,
        )


@pytest.mark.django_db
def test_get_client_by_email_success(client_service: BaseClientService, client_create):
    client = client_create()
    found_client = client_service.get_by_email(
        client_email=client.email,
    )
    assert found_client.email == client.email


@pytest.mark.django_db
def test_get_client_by_id_success(client_service: BaseClientService, client_create):
    client = client_create()
    found_client = client_service.get_by_id(
        client_id=client.id,
    )
    assert found_client.email == client.email
    assert found_client.id == client.id


@pytest.mark.django_db
def test_get_client_by_email_not_found_failure(client_service: BaseClientService, client_build):
    client = client_build()
    with pytest.raises(ClientNotFoundException):
        client_service.get_by_email(client_email=client.email)


@pytest.mark.django_db
def test_get_client_by_id_not_found_failure(client_service: BaseClientService, client_build):
    client = client_build()
    with pytest.raises(ClientNotFoundException):
        client_service.get_by_id(client_id=client.id)


@pytest.mark.django_db
def test_client_update_email_success(client_service: BaseClientService, client_create, generate_email):
    client = client_create()
    new_email = generate_email()
    client_service.update_email(client_id=client.id, email=new_email)
    updated_client = client_service.get_by_id(client.id)

    assert updated_client.email == new_email
    assert updated_client.email != client.email


@pytest.mark.django_db
def test_client_update_email_failure(client_service: BaseClientService, client_build, generate_email):
    client = client_build()
    new_email = generate_email()

    with pytest.raises(ClientUpdateException):
        client_service.update_email(client_id=client.id, email=new_email)


@pytest.mark.django_db
def test_client_update_password_success(
        client_service: BaseClientService,
        create_client_with_password,
        build_client_with_password,
):
    client, plain_password = create_client_with_password
    new_client, new_plain_password = build_client_with_password
    client_service.update_password(client_id=client.id, hashed_password=new_client.password)

    stored_hash = client_service.get_password_hash_by_email(client_email=client.email)
    assert stored_hash == new_client.password
    assert stored_hash != client.password


@pytest.mark.django_db
def test_client_update_password_failure(client_service: BaseClientService, client_build, generate_password):
    client = client_build()
    password = generate_password()
    with pytest.raises(ClientUpdateException):
        client_service.update_password(client_id=client.id, hashed_password=password)


@pytest.mark.django_db
def test_client_update_credentials_success(client_service: BaseClientService, client_create, faker_ua):
    client = client_create()
    new_first_name = faker_ua.first_name()
    new_last_name = faker_ua.last_name()
    new_middle_name = faker_ua.last_name()

    client_service.update_credentials(
        client_id=client.id,
        first_name=new_first_name,
        last_name=new_last_name,
        middle_name=new_middle_name,
    )
    updated_client = client_service.get_by_id(client.id)

    assert updated_client.first_name == new_first_name, f'{new_first_name=}'
    assert updated_client.last_name == new_last_name, f'{new_last_name=}'
    assert updated_client.middle_name == new_middle_name, f'{new_middle_name=}'


@pytest.mark.django_db
def test_client_update_credentials_failure(client_service: BaseClientService, client_build, faker_ua):
    client = client_build()
    new_first_name = faker_ua.first_name()
    new_last_name = faker_ua.last_name()
    new_middle_name = faker_ua.last_name()

    with pytest.raises(ClientUpdateException):
        client_service.update_credentials(
            client_id=client.id,
            first_name=new_first_name,
            last_name=new_last_name,
            middle_name=new_middle_name,
        )


@pytest.mark.django_db
def test_client_update_role_success(client_service: BaseClientService, client_create):
    client = client_create(roles=[RoleModelFactory(id=ClientRole.HEADMAN)])
    client_service.update_roles(client_id=client.id, roles=[RoleModelFactory(id=ClientRole.ADMIN)])
    updated_client = client_service.get_by_id(client.id)
    assert updated_client.roles == [ClientRole(role.id) for role in client.roles.all()]
    assert updated_client.roles == [ClientRole.ADMIN]


@pytest.mark.django_db
def test_client_update_role_failure(client_service: BaseClientService, client_build):
    client = client_build()

    with pytest.raises(ClientUpdateException):
        client_service.update_roles(client_id=client.id, roles=[ClientRole.ADMIN])
