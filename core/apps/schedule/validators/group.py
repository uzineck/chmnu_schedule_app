from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.schedule.exceptions.group import (
    GroupAlreadyExistsException,
    HeadmanAssignedToAnotherGroupException,
)
from core.apps.schedule.services.group import BaseGroupService


class BaseGroupValidatorService(ABC):

    @abstractmethod
    def validate(
            self,
            group_number: str | None = None,
            headman: ClientEntity | None = None,
    ):
        ...


@dataclass
class GroupAlreadyExistsValidatorService(BaseGroupValidatorService):
    group_service: BaseGroupService

    def validate(self, group_number: str | None = None, *args, **kwargs):
        if group_number:
            if self.group_service.check_exists_by_number(group_number=group_number):
                raise GroupAlreadyExistsException(group_number=group_number)


@dataclass
class HeadmanAssignedToAnotherGroupValidatorService(BaseGroupValidatorService):
    group_service: BaseGroupService

    def validate(self, headman: ClientEntity | None = None, *args, **kwargs):
        if headman:
            if self.group_service.check_if_headman_assigned_to_group(headman_id=headman.id):
                raise HeadmanAssignedToAnotherGroupException(headman_email=headman.email)


@dataclass
class ComposedGroupValidatorService(BaseGroupValidatorService):
    validators: list[BaseGroupValidatorService]

    def validate(
            self,
            group_number: str | None = None,
            headman: ClientEntity | None = None,
    ):
        for validator in self.validators:
            validator.validate(group_number=group_number, headman=headman)
