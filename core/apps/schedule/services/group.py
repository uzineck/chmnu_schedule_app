from django.db import IntegrityError
from django.utils import timezone

from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.common.models import Subgroup
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.exceptions.group import (
    GroupAlreadyExistsException,
    GroupHeadmanUpdateException,
    GroupNotFoundException,
    GroupWithoutSubgroupsInvalidSubgroupException,
    GroupWithSubgroupsInvalidSubgroupException,
    HeadmanNotAssignedToAnyGroup,
)
from core.apps.schedule.models.group import Group as GroupModel


class BaseGroupService(ABC):
    @abstractmethod
    def create(
        self,
        group_number: str,
        faculty_id: int,
        has_subgroups: bool,
        headman_id: int,
    ) -> GroupEntity:
        ...

    @abstractmethod
    def get_all(self) -> Iterable[GroupEntity]:
        ...

    @abstractmethod
    def get_by_uuid(self, group_uuid: str) -> GroupEntity:
        ...

    @abstractmethod
    def get_by_id(self, group_id: int) -> GroupEntity:
        ...

    @abstractmethod
    def check_exists_by_number(self, group_number: str) -> bool:
        ...

    @abstractmethod
    def validate_subgroup_for_group(self, group: GroupEntity, subgroup: Subgroup | None) -> None:
        ...

    @abstractmethod
    def check_if_headman_assigned_to_group(self, headman_id: int) -> bool:
        ...

    @abstractmethod
    def get_group_from_headman(self, headman_id: int) -> GroupEntity:
        ...

    @abstractmethod
    def update_group_headman(self, group_id: int, headman_id: int) -> None:
        ...

    @abstractmethod
    def bump_schedule_updated_at(self, group_id: int) -> None:
        ...

    @abstractmethod
    def find_any_by_number(self, group_number: str) -> GroupEntity | None:
        ...

    @abstractmethod
    def check_faculty_has_groups(self, faculty_id: int) -> bool:
        ...

    @abstractmethod
    def soft_delete(self, group_id: int) -> None:
        ...

    @abstractmethod
    def restore(self, group_id: int) -> None:
        ...


class ORMGroupService(BaseGroupService):
    def create(
        self,
        group_number: str,
        faculty_id: int,
        has_subgroups: bool,
        headman_id: int,
    ) -> GroupEntity:
        try:
            group = GroupModel.objects.create(
                number=group_number,
                faculty_id=faculty_id,
                has_subgroups=has_subgroups,
                headman_id=headman_id,
            )
        except IntegrityError:
            raise GroupAlreadyExistsException(group_number=group_number, headman_id=headman_id)

        return group.to_entity()

    def get_all(self) -> list[GroupEntity]:
        groups = (
            GroupModel.objects.
            all().
            select_related("headman", "faculty")
        )
        return [group.to_entity() for group in groups]

    def get_by_uuid(self, group_uuid: str) -> GroupEntity:
        try:
            group = (
                GroupModel.objects.
                select_related("headman", "faculty").
                get(group_uuid=group_uuid)
            )
        except GroupModel.DoesNotExist:
            raise GroupNotFoundException(uuid=group_uuid)

        return group.to_entity()

    def get_by_id(self, group_id: int) -> GroupEntity:
        try:
            group = (
                GroupModel.objects.
                select_related("headman", "faculty").
                get(id=group_id)
            )
        except GroupModel.DoesNotExist:
            raise GroupNotFoundException(id=group_id)

        return group.to_entity()

    def check_exists_by_number(self, group_number: str) -> bool:
        return GroupModel.objects.filter(number=group_number).exists()

    def validate_subgroup_for_group(self, group: GroupEntity, subgroup: Subgroup | None) -> None:
        if not group.has_subgroups and subgroup is not None:
            raise GroupWithoutSubgroupsInvalidSubgroupException(subgroup=subgroup)

        if group.has_subgroups and subgroup is None:
            raise GroupWithSubgroupsInvalidSubgroupException

    def check_if_headman_assigned_to_group(self, headman_id: int) -> bool:
        return GroupModel.objects.filter(headman__id=headman_id).exists()

    def get_group_from_headman(self, headman_id: int) -> GroupEntity:
        group: GroupModel = (
            GroupModel.objects.filter(headman__id=headman_id).
            select_related("headman", "faculty").
            first()
        )

        if not group:
            raise HeadmanNotAssignedToAnyGroup(headman_id=headman_id)

        return group.to_entity()

    def update_group_headman(self, group_id: int, headman_id: int) -> None:
        is_updated = GroupModel.objects.filter(id=group_id).update(headman_id=headman_id)

        if not is_updated:
            raise GroupHeadmanUpdateException(group_id=group_id, headman_id=headman_id)

    def bump_schedule_updated_at(self, group_id: int) -> None:
        GroupModel.objects.filter(id=group_id).update(schedule_updated_at=timezone.now())

    def find_any_by_number(self, group_number: str) -> GroupEntity | None:
        group = (
            GroupModel.all_objects.
            select_related("headman", "faculty").
            filter(number=group_number).
            first()
        )
        return group.to_entity() if group is not None else None

    def check_faculty_has_groups(self, faculty_id: int) -> bool:
        return GroupModel.objects.filter(faculty_id=faculty_id).exists()

    def soft_delete(self, group_id: int) -> None:
        GroupModel.objects.filter(id=group_id).update(is_active=False)

    def restore(self, group_id: int) -> None:
        GroupModel.all_objects.filter(id=group_id).update(is_active=True)
