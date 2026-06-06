import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.schedule.group import GroupModelFactory

from core.apps.schedule.exceptions.group import (
    GroupHeadmanUpdateException,
    HeadmanNotAssignedToAnyGroup,
)
from core.apps.schedule.services.group import BaseGroupService


@pytest.fixture
def group_service(container) -> BaseGroupService:
    return container.resolve(BaseGroupService)


@pytest.mark.django_db
def test_get_group_from_headman_returns_group(group_service: BaseGroupService):
    headman = ClientModelFactory()
    group = GroupModelFactory(headman=headman)

    result = group_service.get_group_from_headman(headman_id=headman.id)

    assert result.uuid == str(group.group_uuid)


@pytest.mark.django_db
def test_get_group_from_headman_raises_when_no_assignment(group_service: BaseGroupService):
    client = ClientModelFactory()

    with pytest.raises(HeadmanNotAssignedToAnyGroup):
        group_service.get_group_from_headman(headman_id=client.id)


@pytest.mark.django_db
def test_update_group_headman_happy_path(group_service: BaseGroupService):
    group = GroupModelFactory()
    new_headman = ClientModelFactory()

    group_service.update_group_headman(group_id=group.id, headman_id=new_headman.id)

    group.refresh_from_db()
    assert group.headman_id == new_headman.id


@pytest.mark.django_db
def test_update_group_headman_raises_when_group_id_missing(group_service: BaseGroupService):
    client = ClientModelFactory()

    with pytest.raises(GroupHeadmanUpdateException):
        group_service.update_group_headman(group_id=99999, headman_id=client.id)


@pytest.mark.django_db
def test_find_any_by_number_returns_active_group(group_service: BaseGroupService):
    group = GroupModelFactory(number="ПМ-201")

    found = group_service.find_any_by_number(group_number="ПМ-201")

    assert found is not None
    assert found.id == group.id
    assert found.is_active is True


@pytest.mark.django_db
def test_find_any_by_number_returns_soft_deleted_group(group_service: BaseGroupService):
    group = GroupModelFactory(number="ПМ-301")
    group_service.soft_delete(group_id=group.id)

    found = group_service.find_any_by_number(group_number="ПМ-301")

    assert found is not None
    assert found.id == group.id
    assert found.is_active is False


@pytest.mark.django_db
def test_find_any_by_number_returns_none_when_missing(group_service: BaseGroupService):
    assert group_service.find_any_by_number(group_number="DOES-NOT-EXIST") is None


@pytest.mark.django_db
def test_restore_reactivates_soft_deleted_group(group_service: BaseGroupService):
    group = GroupModelFactory()
    group_service.soft_delete(group_id=group.id)

    group_service.restore(group_id=group.id)

    group.refresh_from_db()
    assert group.is_active is True
