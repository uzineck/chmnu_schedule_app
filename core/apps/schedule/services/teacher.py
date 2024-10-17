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
    def update_is_active(
            self,
            teacher_id: int,
            is_active: bool,
    ) -> None:
        ...


class ORMTeacherService(BaseTeacherService):
    def _build_teacher_query(self, filters: TeacherFilter) -> Q:
        query = Q(is_active=True)

        if filters.first_name is not None:
            query &= (Q(first_name__icontains=filters.first_name))
        if filters.last_name is not None:
            query &= (Q(last_name__icontains=filters.last_name))
        if filters.middle_name is not None:
            query &= (Q(middle_name__icontains=filters.middle_name))
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

    def get_all(self) -> Iterable[TeacherEntity]:
        teachers = TeacherModel.objects.filter(is_active=True).all()

        for teacher in teachers:
            yield teacher.to_entity()

    def get_by_uuid(self, teacher_uuid: str) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.get(teacher_uuid=teacher_uuid, is_active=True)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(uuid=teacher_uuid)

        return teacher.to_entity()

    def get_by_id(self, teacher_id: int) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.get(id=teacher_id, is_active=True)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(id=teacher_id)

        return teacher.to_entity()

    def get_list(self, filters: TeacherFilter, pagination: PaginationIn) -> Iterable[TeacherEntity]:
        query = self._build_teacher_query(filters)
        qs = TeacherModel.objects.filter(query)[pagination.offset:pagination.offset + pagination.limit]
        return [teacher.to_entity() for teacher in qs]

    def get_count(self, filters: TeacherFilter) -> int:
        query = self._build_teacher_query(filters)

        return TeacherModel.objects.filter(query).count()

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

    def update_is_active(
            self,
            teacher_id: int,
            is_active: bool,
    ) -> None:
        is_updated = TeacherModel.objects.filter(id=teacher_id).update(is_active=is_active)

        if not is_updated:
            raise TeacherUpdateException(id=teacher_id)
