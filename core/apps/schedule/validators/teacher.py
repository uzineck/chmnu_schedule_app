from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.common.models import TeachersDegree
from core.apps.schedule.exceptions.teacher import (
    OldAndNewTeacherNamesAreSimilarException,
    OldAndNewTeacherRanksAreSimilarException,
    TeacherAlreadyExistsException,
)
from core.apps.schedule.services.teacher import BaseTeacherService


class BaseTeacherValidatorService(ABC):

    @abstractmethod
    def validate(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            middle_name: str | None = None,
            rank: TeachersDegree | None = None,
            old_first_name: str | None = None,
            old_last_name: str | None = None,
            old_middle_name: str | None = None,
            old_rank: TeachersDegree | None = None,
    ):
        ...


@dataclass
class TeacherAlreadyExistsValidatorService(BaseTeacherValidatorService):
    teacher_service: BaseTeacherService

    def validate(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            middle_name: str | None = None,
            *args,
            **kwargs,
    ):
        if first_name is not None and last_name is not None and middle_name is not None:
            if self.teacher_service.check_exists_by_full_name(
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
            ):
                raise TeacherAlreadyExistsException(
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
                )


class SimilarOldAndNewTeacherNameValidatorService(BaseTeacherValidatorService):
    def validate(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            middle_name: str | None = None,
            old_first_name: str | None = None,
            old_last_name: str | None = None,
            old_middle_name: str | None = None,
            *args,
            **kwargs,
    ):
        if first_name is not None and last_name is not None and middle_name is not None:
            if first_name == old_first_name and last_name == old_last_name and middle_name == old_middle_name:
                raise OldAndNewTeacherNamesAreSimilarException(
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
                    old_first_name=old_first_name,
                    old_last_name=old_last_name,
                    old_middle_name=old_middle_name,
                )


class SimilarOldAndNewTeacherRanksValidatorService(BaseTeacherValidatorService):
    def validate(
            self,
            rank: TeachersDegree | None = None,
            old_rank: TeachersDegree | None = None,
            *args,
            **kwargs,
    ):
        if rank is not None and old_rank is not None:
            if rank == old_rank:
                raise OldAndNewTeacherRanksAreSimilarException(old_rank=old_rank, new_rank=rank)


@dataclass
class ComposedTeacherValidatorService(BaseTeacherValidatorService):
    validators: list[BaseTeacherValidatorService]

    def validate(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            middle_name: str | None = None,
            rank: TeachersDegree | None = None,
            old_first_name: str | None = None,
            old_last_name: str | None = None,
            old_middle_name: str | None = None,
            old_rank: TeachersDegree | None = None,
    ):
        for validator in self.validators:
            validator.validate(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                rank=rank,
                old_first_name=old_first_name,
                old_last_name=old_last_name,
                old_middle_name=old_middle_name,
                old_rank=old_rank,
            )
