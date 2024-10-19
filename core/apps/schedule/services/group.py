from django.db import IntegrityError

import logging
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
    HeadmanNotAssignedToAnyGroup,
)
from core.apps.schedule.models.group import Group as GroupModel


logger = logging.getLogger(__name__)


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
    def check_if_group_has_subgroup(self, group: GroupEntity, subgroup: Subgroup) -> bool:
        ...

    @abstractmethod
    def get_group_list_from_lesson(self, lesson_id: int) -> Iterable[GroupEntity]:
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
            logger.error(f"Group Creation Error ({group_number=}, {headman_id=})")
            raise GroupAlreadyExistsException(group_number=group_number, headman_id=headman_id)

        return group.to_entity()

    def get_all(self) -> Iterable[GroupEntity]:
        groups = (
            GroupModel.objects.
            all().
            select_related("headman", "faculty")
        )
        for group in groups:
            yield group.to_entity()

    def get_by_uuid(self, group_uuid: str) -> GroupEntity:
        try:
            group = (
                GroupModel.objects.
                select_related("headman", "faculty").
                get(group_uuid=group_uuid)
            )
        except GroupModel.DoesNotExist:
            logger.error(f"Group Does Not Exist Error ({group_uuid=})")
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
            logger.error(f"Group Does Not Exist Error ({group_id=})")
            raise GroupNotFoundException(id=group_id)

        return group.to_entity()

    def check_exists_by_number(self, group_number: str) -> bool:
        return GroupModel.objects.filter(number=group_number).exists()

    def check_if_group_has_subgroup(self, group: GroupEntity, subgroup: Subgroup) -> bool:
        if not group.has_subgroups and subgroup != Subgroup.A:
            logger.warning(
                f"Group Does Not Has Subgroup Error "
                f"(group_number={group.number}, group_has_subgroups={group.has_subgroups}, {subgroup=})",
            )
            raise GroupWithoutSubgroupsInvalidSubgroupException(subgroup=subgroup)

        return True

    def get_group_list_from_lesson(self, lesson_id: int) -> Iterable[GroupEntity]:
        groups = (
            GroupModel.objects.
            filter(group__lesson_id=lesson_id).
            select_related("headman", "faculty")
        )

        return [group.to_entity() for group in groups]

    def check_if_headman_assigned_to_group(self, headman_id: int) -> bool:
        return GroupModel.objects.filter(headman__id=headman_id).exists()

    def get_group_from_headman(self, headman_id: int) -> GroupEntity:
        group: GroupModel = (
            GroupModel.objects.filter(headman__id=headman_id).
            select_related("headman", "faculty").
            first()
        )

        if not group:
            logger.error(f"Headman Not Assigned To Any Group Error ({headman_id=})")
            raise HeadmanNotAssignedToAnyGroup(headman_id=headman_id)

        return group.to_entity()

    def update_group_headman(self, group_id: int, headman_id: int) -> None:
        is_updated = GroupModel.objects.filter(id=group_id).update(headman_id=headman_id)

        if not is_updated:
            logger.error(f"Group Update Headman Error ({group_id=}, {headman_id=})")
            raise GroupHeadmanUpdateException(group_id=group_id, headman_id=headman_id)
