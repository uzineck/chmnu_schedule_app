from django.core.cache import cache

import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory

from core.api.filters import PaginationIn
from core.apps.clients.filters.client import ClientSearchFilter
from core.apps.clients.usecases.admin.get_all import GetAllClientsUseCase
from core.apps.clients.usecases.admin.get_list import GetClientListUseCase
from core.apps.common.models import ClientRole


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def get_list_use_case(container) -> GetClientListUseCase:
    return container.resolve(GetClientListUseCase)


@pytest.fixture
def get_all_use_case(container) -> GetAllClientsUseCase:
    return container.resolve(GetAllClientsUseCase)


@pytest.fixture
def seed_roles_and_clients():
    """Three clients across roles: HEADMAN, ADMIN, CLIENT_MANAGER."""
    headman_role = RoleModelFactory(id=ClientRole.HEADMAN)
    admin_role = RoleModelFactory(id=ClientRole.ADMIN)
    cm_role = RoleModelFactory(id=ClientRole.CLIENT_MANAGER)

    headman = ClientModelFactory(roles=[headman_role], last_name="Aaa")
    admin = ClientModelFactory(roles=[admin_role], last_name="Bbb")
    cm = ClientModelFactory(roles=[cm_role], last_name="Ccc")

    return {"headman": headman, "admin": admin, "cm": cm}


# --- GetList (paginated) ---

@pytest.mark.django_db
def test_get_client_list_admin_sees_all(get_list_use_case, seed_roles_and_clients):
    items, count = get_list_use_case.execute(
        filters=ClientSearchFilter(),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    assert count == 3
    assert len(list(items)) == 3


@pytest.mark.django_db
def test_get_client_list_client_manager_sees_only_headmen(get_list_use_case, seed_roles_and_clients):
    items, count = get_list_use_case.execute(
        filters=ClientSearchFilter(allowed_roles=(ClientRole.HEADMAN,)),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    items = list(items)
    assert count == 1
    assert {r for c in items for r in c.roles} == {ClientRole.HEADMAN}


@pytest.mark.django_db
def test_get_client_list_search_filters_by_email(get_list_use_case):
    headman_role = RoleModelFactory(id=ClientRole.HEADMAN)
    ClientModelFactory(email="foo@gmail.com", roles=[headman_role])
    ClientModelFactory(email="bar@gmail.com", roles=[headman_role])

    items, count = get_list_use_case.execute(
        filters=ClientSearchFilter(search="foo"),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    items = list(items)
    assert count == 1
    assert items[0].email == "foo@gmail.com"


@pytest.mark.django_db
def test_get_client_list_search_filters_by_last_name(get_list_use_case):
    headman_role = RoleModelFactory(id=ClientRole.HEADMAN)
    ClientModelFactory(last_name="Шевченко", roles=[headman_role])
    ClientModelFactory(last_name="Франко", roles=[headman_role])

    items, count = get_list_use_case.execute(
        filters=ClientSearchFilter(search="Шевч"),
        pagination_in=PaginationIn(offset=0, limit=10),
    )

    items = list(items)
    assert count == 1
    assert items[0].last_name == "Шевченко"


# --- GetAll (non-paginated) ---

@pytest.mark.django_db
def test_get_all_clients_admin_sees_all(get_all_use_case, seed_roles_and_clients):
    items = get_all_use_case.execute(filters=ClientSearchFilter())

    assert len(items) == 3


@pytest.mark.django_db
def test_get_all_clients_client_manager_sees_only_headmen(get_all_use_case, seed_roles_and_clients):
    items = get_all_use_case.execute(
        filters=ClientSearchFilter(allowed_roles=(ClientRole.HEADMAN,)),
    )

    assert len(items) == 1
    assert ClientRole.HEADMAN in items[0].roles
