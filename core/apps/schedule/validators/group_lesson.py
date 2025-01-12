from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.services.client import BaseClientService
from core.apps.common.models import (
    ClientRole,
    Subgroup,
)
from core.apps.schedule.entities.group import Group
from core.apps.schedule.entities.group_lessons import GroupLesson
from core.apps.schedule.exceptions.group_lesson import GroupLessonAlreadyExists
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.group_lessons import BaseGroupLessonService


class BaseGroupLessonValidatorService(ABC):

    @abstractmethod
    def validate(
            self,
            client_roles: list[ClientRole] | None = None,
            required_role: ClientRole | None = None,
            group: Group | None = None,
            subgroup: Subgroup | None = None,
            group_lesson: GroupLesson | None = None,
    ):
        ...


@dataclass
class CheckGroupHasSubgroupValidatorService(BaseGroupLessonValidatorService):
    group_service: BaseGroupService

    def validate(self, group: Group | None = None, subgroup: Subgroup | None = None, *args, **kwargs):
        if group:
            self.group_service.check_if_group_has_subgroup(group=group, subgroup=subgroup)


@dataclass
class ClientDoesNotMatchRolesValidatorService(BaseGroupLessonValidatorService):
    client_service: BaseClientService

    def validate(
            self,
            client_roles: list[ClientRole] | None = None,
            required_role: ClientRole | None = None,
            *args,
            **kwargs,
    ):
        if client_roles and required_role:
            self.client_service.check_client_role(client_roles=client_roles, required_role=required_role)


@dataclass
class CheckLessonInGroupAlreadyExistsValidatorService(BaseGroupLessonValidatorService):
    group_lesson_service: BaseGroupLessonService

    def validate(self, group_lesson: GroupLesson | None = None, *args, **kwargs):
        if group_lesson:
            if self.group_lesson_service.check_exists(group_lesson=group_lesson):
                raise GroupLessonAlreadyExists(
                    group_uuid=group_lesson.group.uuid,
                    lesson_uuid=group_lesson.lesson.uuid,
                    subgroup=group_lesson.subgroup,
                )


@dataclass
class ComposedGroupLessonValidatorService(BaseGroupLessonValidatorService):
    validators: list[BaseGroupLessonValidatorService]

    def validate(
            self,
            client_roles: list[ClientRole] | None = None,
            required_role: ClientRole | None = None,
            group: Group | None = None,
            subgroup: Subgroup | None = None,
            group_lesson: GroupLesson | None = None,
    ):
        for validator in self.validators:
            validator.validate(
                client_roles=client_roles,
                required_role=required_role,
                group=group,
                subgroup=subgroup,
                group_lesson=group_lesson,
            )
