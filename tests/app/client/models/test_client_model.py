from django.db import IntegrityError

import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.common.models import ClientRole


@pytest.mark.django_db
def test_client_create():
    client = ClientModelFactory.create(
        first_name="Іван",
        last_name="Шевченко",
        middle_name="Олегович",
        email="ivan@gmail.com",
    )

    assert client.pk is not None
    assert client.first_name == "Іван"
    assert client.last_name == "Шевченко"
    assert client.middle_name == "Олегович"
    assert client.email == "ivan@gmail.com"
    assert client.created_at is not None
    assert client.updated_at is not None


@pytest.mark.django_db
def test_client_email_unique_constraint():
    ClientModelFactory.create(email="dup@gmail.com")

    with pytest.raises(IntegrityError):
        ClientModelFactory.create(email="dup@gmail.com")


@pytest.mark.django_db
def test_client_factory_assigns_default_role():
    client = ClientModelFactory.create()

    assert client.roles.filter(id=ClientRole.DEFAULT).exists()


@pytest.mark.django_db
def test_client_to_entity_maps_all_fields():
    role = RoleModelFactory.create(id=ClientRole.ADMIN)
    client = ClientModelFactory.create(
        first_name="Олена",
        last_name="Бондаренко",
        middle_name="Василівна",
        email="olena@gmail.com",
        roles=[role],
    )

    entity = client.to_entity()

    assert isinstance(entity, ClientEntity)
    assert entity.id == client.id
    assert entity.first_name == "Олена"
    assert entity.last_name == "Бондаренко"
    assert entity.middle_name == "Василівна"
    assert entity.email == "olena@gmail.com"
    assert ClientRole.ADMIN in entity.roles
    assert entity.created_at == client.created_at
    assert entity.updated_at == client.updated_at


def test_client_str_full_name():
    client = ClientModelFactory.build(
        first_name="Іван",
        last_name="Шевченко",
        middle_name="Олегович",
    )

    assert str(client) == "Шевченко І. О."


def test_client_str_missing_middle_name():
    client = ClientModelFactory.build(
        first_name="Іван",
        last_name="Шевченко",
        middle_name="",
    )

    assert str(client) == "Шевченко І."


def test_client_str_missing_first_name():
    client = ClientModelFactory.build(
        first_name="",
        last_name="Шевченко",
        middle_name="Олегович",
    )

    assert str(client) == "Шевченко О."
