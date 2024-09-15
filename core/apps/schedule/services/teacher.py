from django.db.models import Q

from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.api.filters import PaginationIn
from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.exceptions.subject import SubjectIdNotFoundException
from core.apps.schedule.exceptions.teacher import TeacherNotFoundException
from core.apps.schedule.filters.teacher import TeacherFilter
from core.apps.schedule.models import Subject as SubjectModel
from core.apps.schedule.models.teacher import Teacher as TeacherModel


class BaseTeacherService(ABC):
    @abstractmethod
    def get_or_create(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
            rank: TeachersDegree,
    ) -> TeacherEntity:
        ...

    @abstractmethod
    def get_teacher_by_id(self, teacher_id: int) -> TeacherEntity:
        ...

    @abstractmethod
    def get_teacher_list(self, filters: TeacherFilter, pagination: PaginationIn) -> Iterable[TeacherEntity]:
        ...

    @abstractmethod
    def get_teacher_count(self, filters: TeacherFilter) -> int:
        ...

    @abstractmethod
    def get_qs_for_teacher(self, filters: TeacherFilter) -> Q:
        ...

    @abstractmethod
    def update_teacher_by_id(
            self,
            teacher_id: int,
            first_name: str,
            last_name: str,
            middle_name: str,
            rank: str,
    ) -> TeacherEntity:
        ...

    @abstractmethod
    def add_teacher_subject(self, teacher_id: int, subject_id: int) -> TeacherEntity:
        ...

    @abstractmethod
    def remove_teacher_subject(self, teacher_id: int, subject_id: int) -> TeacherEntity:
        ...


class ORMTeacherService(BaseTeacherService):
    def _build_teacher_query(self, filters: TeacherFilter) -> Q:
        query = Q(is_active=True)

        if filters.name is not None:
            query &= (
                Q(first_name__icontains=filters.name) |
                Q(last_name__icontains=filters.name) |
                Q(middle_name__icontains=filters.name)
            )
        if filters.rank is not None:
            query &= (Q(rank__icontains=filters.rank))

        return query

    def get_or_create(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
            rank: str,
    ) -> TeacherEntity:
        teacher, _ = TeacherModel.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            rank=rank,
        )

        return teacher.to_entity()

    def get_teacher_by_id(self, teacher_id: int) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.get(id=teacher_id)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(id=teacher_id)

        return teacher.to_entity()

    def get_teacher_list(self, filters: TeacherFilter, pagination: PaginationIn) -> Iterable[TeacherEntity]:
        query = self._build_teacher_query(filters)
        qs = TeacherModel.objects.filter(query)[pagination.offset:pagination.offset + pagination.limit]
        return [teacher.to_entity() for teacher in qs]

    def get_teacher_count(self, filters: TeacherFilter) -> int:
        query = self._build_teacher_query(filters)

        return TeacherModel.objects.filter(query).count()

    def get_qs_for_teacher(self, filters: TeacherFilter) -> Q:
        query = self._build_teacher_query(filters)

        return query

    def update_teacher_by_id(
            self,
            teacher_id: int,
            first_name: str,
            last_name: str,
            middle_name: str,
            rank: str,
    ) -> TeacherEntity:

        TeacherModel.objects.filter(id=teacher_id).update(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            rank=rank,
        )
        try:
            teacher = TeacherModel.objects.get(id=teacher_id)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(id=teacher_id)

        return teacher.to_entity()

    def add_teacher_subject(self, teacher_id: int, subject_id: int) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.get(id=teacher_id)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(id=teacher_id)

        try:
            subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            raise SubjectIdNotFoundException(subject_id=subject_id)

        teacher.subjects.add(subject)
        return teacher.to_entity()

    def remove_teacher_subject(self, teacher_id: int, subject_id: int) -> TeacherEntity:
        try:
            teacher = TeacherModel.objects.get(id=teacher_id)
        except TeacherModel.DoesNotExist:
            raise TeacherNotFoundException(id=teacher_id)

        try:
            subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            raise SubjectIdNotFoundException(subject_id=subject_id)

        teacher.subjects.remove(subject)
        return teacher.to_entity()
