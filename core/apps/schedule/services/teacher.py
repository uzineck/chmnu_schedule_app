from django.db import IntegrityError
from django.db.models import Q

from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.api.filters import PaginationIn
from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.exceptions.teacher import (
    TeacherAlreadyExistsException,
    TeacherDeleteException,
    TeacherNotFoundException,
    TeacherUpdateException,
)
from core.apps.schedule.filters.teacher import TeacherFilter
from core.apps.schedule.models.teacher import Teacher as TeacherModel


class BaseTeacherService(ABC):
    @abstractmethod
    def create(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
            rank: TeachersDegree,
    ) -> TeacherEntity:
        ...

    @abstractmethod
    def get_all(self) -> Iterable[TeacherEntity]:
        ...

    @abstractmethod
    def get_list(self, filters: TeacherFilter, pagination: PaginationIn) -> Iterable[TeacherEntity]:
        ...

    @abstractmethod
    def get_count(self, filters: TeacherFilter) -> int:
        ...

    @abstractmethod
    def get_by_uuid(self, teacher_uuid: str) -> TeacherEntity:
        ...

    @abstractmethod
    def get_by_id(self, teacher_id: int) -> TeacherEntity:
        ...

    @abstractmethod
    def check_exists_by_full_name(self, first_name: str, last_name: str, middle_name: str) -> bool:
        ...

    @abstractmethod
    def find_any_by_full_name(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
    ) -> TeacherEntity | None:
        ...

    @abstractmethod
    def update_name(
            self,
            teacher_id: int,
            first_name: str,
            last_name: str,
            middle_name: str,
    ) -> None:
        ...

    @abstractmethod
    def update_rank(
            self,
            teacher_id: int,
            rank: TeachersDegree,
    ) -> None:
        ...

    @abstractmethod
    def soft_delete(self, teacher_id: int) -> None:
        ...

    @abstractmethod
    def restore(self, teacher_id: int) -> None:
        ...


class ORMTeacherService(BaseTeacherService):
    def _build_teacher_query(self, filters: TeacherFilter) -> Q:
        query = Q()

        if filters.name is not None:
            for token in filters.name.split():
                query &= (
                    Q(first_name__icontains=token) |
                    Q(last_name__icontains=token) |
                    Q(middle_name__icontains=token)
                )
        if filters.rank is not None:
            query &= (Q(rank__icontains=filters.rank))

        return query

    def create(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
            rank: str,
    ) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                rank=rank,
            )
        except IntegrityError:
            raise TeacherAlreadyExistsException(first_name=first_name, last_name=last_name, middle_name=middle_name)

        return teacher.to_entity()

    def get_all(self) -> list[TeacherEntity]:
        return [teacher.to_entity() for teacher in TeacherModel.objects.all()]

    def get_list(self, filters: TeacherFilter, pagination: PaginationIn) -> list[TeacherEntity]:
        query = self._build_teacher_query(filters)
        qs = TeacherModel.objects.filter(query)[pagination.offset:pagination.offset + pagination.limit]
        return [teacher.to_entity() for teacher in qs]

    def get_count(self, filters: TeacherFilter) -> int:
        query = self._build_teacher_query(filters)

        return TeacherModel.objects.filter(query).count()

    def get_by_uuid(self, teacher_uuid: str) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.get(teacher_uuid=teacher_uuid)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(uuid=teacher_uuid)

        return teacher.to_entity()

    def get_by_id(self, teacher_id: int) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.get(id=teacher_id)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(id=teacher_id)

        return teacher.to_entity()

    def check_exists_by_full_name(self, first_name: str, last_name: str, middle_name: str) -> bool:
        return TeacherModel.objects.filter(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        ).exists()

    def find_any_by_full_name(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
    ) -> TeacherEntity | None:
        teacher = TeacherModel.all_objects.filter(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        ).first()
        return teacher.to_entity() if teacher is not None else None

    def update_name(
            self,
            teacher_id: int,
            first_name: str,
            last_name: str,
            middle_name: str,
    ) -> None:
        is_updated = TeacherModel.objects.filter(id=teacher_id).update(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        if not is_updated:
            raise TeacherUpdateException(id=teacher_id)

    def update_rank(
            self,
            teacher_id: int,
            rank: TeachersDegree,
    ) -> None:
        is_updated = TeacherModel.objects.filter(id=teacher_id).update(
            rank=rank,
        )
        if not is_updated:
            raise TeacherUpdateException(id=teacher_id)

    def soft_delete(self, teacher_id: int) -> None:
        is_updated = TeacherModel.objects.filter(id=teacher_id).update(is_active=False)

        if not is_updated:
            raise TeacherDeleteException(id=teacher_id)

    def restore(self, teacher_id: int) -> None:
        TeacherModel.all_objects.filter(id=teacher_id).update(is_active=True)
