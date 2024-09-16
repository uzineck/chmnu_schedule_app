from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.exceptions.group import (
    GroupNumberNotFoundException,
    GroupUuidNotFoundException,
)
from core.apps.schedule.models.group import Group as GroupModel


class BaseGroupService(ABC):
    @abstractmethod
    def create(
        self,
        group_number: str,
        has_subgroups: bool,
        headman_id: int,
    ) -> GroupEntity:
        ...

    @abstractmethod
    def get_group_by_number(self, group_number: str) -> GroupEntity:
        ...

    @abstractmethod
    def get_group_by_uuid(self, group_uuid: str) -> GroupEntity:
        ...

    @abstractmethod
    def check_group_exists_by_number(self, group_number: str) -> bool:
        ...

    @abstractmethod
    def check_group_exists_by_uuid(self, group_uuid: str) -> bool:
        ...

    @abstractmethod
    def get_all_groups(self) -> Iterable[GroupEntity]:
        ...

    @abstractmethod
    def update_group_headman(self, group: GroupEntity, headman: ClientEntity) -> GroupEntity:
        ...

    @abstractmethod
    def get_group_from_headman(self, headman: ClientEntity) -> GroupEntity | None:
        ...

    @abstractmethod
    def get_groups_from_lesson(self, lesson_id: int) -> Iterable[GroupEntity]:
        ...


class ORMGroupService(BaseGroupService):

    def create(
        self,
        group_number: str,
        has_subgroups: bool,
        headman_id: int,
    ) -> GroupEntity:
        group = GroupModel.objects.create(
            number=group_number,
            has_subgroups=has_subgroups,
            headman_id=headman_id,
        )

        return group.to_entity()

    def get_group_by_number(self, group_number: str) -> GroupEntity:
        try:
            group = GroupModel.objects.get(number=group_number)
        except GroupModel.DoesNotExist:
            raise GroupNumberNotFoundException(group_number=group_number)

        return group.to_entity()

    def get_group_by_uuid(self, group_uuid: str) -> GroupEntity:
        try:
            group = GroupModel.objects.get(group_uuid=group_uuid)
        except GroupModel.DoesNotExist:
            raise GroupUuidNotFoundException(uuid=group_uuid)

        return group.to_entity()

    def check_group_exists_by_number(self, group_number: str) -> bool:
        return GroupModel.objects.filter(number=group_number).exists()

    def check_group_exists_by_uuid(self, group_uuid: str) -> bool:
        return GroupModel.objects.filter(group_uuid=group_uuid).exists()

    def update_group_headman(self, group: GroupEntity, headman: ClientEntity) -> GroupEntity:
        GroupModel.objects.filter(number=group.number).update(headman_id=headman.id)
        updated_group = GroupModel.objects.get(number=group.number)
        return updated_group.to_entity()

    def get_group_from_headman(self, headman: ClientEntity) -> GroupEntity | None:
        try:
            group = GroupModel.objects.filter(headman__email=headman.email).first()

            return group.to_entity()
        except AttributeError:
            return None

    def get_groups_from_lesson(self, lesson_id: int) -> Iterable[GroupEntity]:
        groups = GroupModel.objects.filter(group_lessons_group__lesson_id=lesson_id)

        return [group.to_entity() for group in groups]

    def get_all_groups(self) -> Iterable[GroupEntity]:
        groups = GroupModel.objects.all()

        for group in groups:
            yield group.to_entity()
