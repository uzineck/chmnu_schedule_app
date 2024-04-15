from abc import ABC, abstractmethod
from typing import Iterable

from core.apps.schedule.entities.group import Group
from core.apps.schedule.models.groups import Group as GroupModel


class BaseGroupService(ABC):
    @abstractmethod
    def get_all_groups(self) -> Iterable[Group]:
        ...


class GroupService(BaseGroupService):
    def get_all_groups(self) -> Iterable[Group]:
        qs = GroupModel.objects.filter()

        return [group.to_entity() for group in qs]


