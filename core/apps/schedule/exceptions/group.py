from dataclasses import dataclass

from core.apps.common.exceptions import ServiceException
from core.apps.common.models import Subgroup


@dataclass(eq=False)
class GroupNotFoundException(ServiceException):
    number: str | None = None
    uuid: str | None = None
    id: int | None = None

    @property
    def message(self):
        return 'Групу з вказаним ідентифікатором не знайдено'


@dataclass(eq=False)
class GroupAlreadyExistsException(ServiceException):
    group_number: str | None = None
    headman_id: int | None = None

    @property
    def message(self):
        return 'Група з вказаними параметрами вже існує'


@dataclass(eq=False)
class HeadmanAssignedToAnotherGroupException(ServiceException):
    headman_email: str

    @property
    def message(self):
        return 'Староста з вказаною електронною адресою вже призначений до іншої групи'


@dataclass(eq=False)
class GroupWithoutSubgroupsInvalidSubgroupException(ServiceException):
    subgroup: Subgroup

    @property
    def message(self):
        return 'Група без підгруп не може мати підгрупу'


@dataclass(eq=False)
class GroupWithSubgroupsInvalidSubgroupException(ServiceException):

    @property
    def message(self):
        return 'Група з підгрупами не може не мати підгрупи'


@dataclass(eq=False)
class HeadmanNotAssignedToAnyGroup(ServiceException):
    headman_id: int

    @property
    def message(self):
        return 'Староста не закріплений за жодною групою'


@dataclass(eq=False)
class GroupHeadmanUpdateException(ServiceException):
    group_id: int | None = None
    headman_id: int | None = None

    @property
    def message(self):
        return 'Виникла помилка під час оновлення старости групи'
