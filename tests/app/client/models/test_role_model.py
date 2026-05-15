from django.db import IntegrityError

import pytest
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.models import Role
from core.apps.common.models import ClientRole


@pytest.mark.django_db
def test_role_create():
    role = RoleModelFactory.create(id=ClientRole.ADMIN)

    assert role.pk == ClientRole.ADMIN


def test_role_str_returns_display_name():
    role = RoleModelFactory.build(id=ClientRole.ADMIN)

    assert str(role) == "Admin"


@pytest.mark.django_db
def test_role_duplicate_pk_raises_integrity_error():
    Role.objects.create(id=ClientRole.HEADMAN)

    with pytest.raises(IntegrityError):
        Role.objects.create(id=ClientRole.HEADMAN)


@pytest.mark.django_db
def test_all_roles_can_be_created():
    for value in ClientRole.values:
        role = RoleModelFactory.create(id=value)
        assert role.pk == value


@pytest.mark.django_db
def test_factory_get_or_create_reuses_existing():
    r1 = RoleModelFactory.create(id=ClientRole.ADMIN)
    r2 = RoleModelFactory.create(id=ClientRole.ADMIN)

    assert r1.pk == r2.pk
    assert Role.objects.filter(id=ClientRole.ADMIN).count() == 1
