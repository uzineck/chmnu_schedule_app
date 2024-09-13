from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.schedule.exceptions.groups import (
    GroupAlreadyExistsException,
    HeadmanAssignedToAnotherGroupException,
)
from core.apps.schedule.services.groups import BaseGroupService


class BaseGroupValidatorService(ABC):
    @abstractmethod
    def validate(
            self,
            group_number: str,
            headman: ClientEntity | None = None,
    ):
        ...


@dataclass
class GroupAlreadyExistsValidatorService(BaseGroupValidatorService):
    group_service: BaseGroupService

    def validate(self, group_number: str, *args, **kwargs):
        if self.group_service.check_group_exists(group_number=group_number):
            raise GroupAlreadyExistsException(group_number=group_number)


@dataclass
class HeadmanAssignedToAnotherGroupValidatorService(BaseGroupValidatorService):
    group_service: BaseGroupService

    def validate(self, group_number: str, headman: ClientEntity | None = None, *args, **kwargs):
        headman_group = self.group_service.get_group_from_headman(headman=headman)
        if (headman_group is not None) and (headman_group != group_number):
            raise HeadmanAssignedToAnotherGroupException(headman_email=headman.email, group_number=group_number)


@dataclass
class ComposedGroupValidatorService(BaseGroupValidatorService):
    validators: list[BaseGroupValidatorService]

    def validate(
            self,
            group_number: str,
            headman: ClientEntity | None = None,
    ):
        for validator in self.validators:
            validator.validate(group_number=group_number, headman=headman)
