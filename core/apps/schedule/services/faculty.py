from django.db import IntegrityError
from django.db.models import Q

from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.exceptions.faculty import (
    FacultyUuidNotFoundException,
    FacultyWithProvidedCodeNameAlreadyExists,
)
from core.apps.schedule.models import Faculty as FacultyModel


class BaseFacultyService(ABC):
    @abstractmethod
    def create(self, name: str, code_name: str) -> FacultyEntity:
        ...

    @abstractmethod
    def get_faculty_list(self, filters: SearchFilterEntity, pagination: PaginationIn) -> Iterable[FacultyEntity]:
        ...

    @abstractmethod
    def get_faculty_count(self, filters: SearchFilterEntity) -> int:
        ...

    @abstractmethod
    def get_faculty_by_uuid(self, faculty_uuid: str) -> FacultyEntity:
        ...


class ORMFacultyService(BaseFacultyService):

    def _build_subject_query(self, filters: SearchFilterEntity) -> Q:
        query = Q()

        if filters.search is not None:
            query &= Q(code_name__icontains=filters.search) | Q(name__icontains=filters.search)

        return query

    def create(self, name: str, code_name: str) -> FacultyEntity:
        try:
            faculty = FacultyModel.objects.create(
                code_name=code_name,
                name=name,
            )
        except IntegrityError:
            raise FacultyWithProvidedCodeNameAlreadyExists(code_name=code_name)

        return faculty.to_entity()

    def get_faculty_list(self, filters: SearchFilterEntity, pagination: PaginationIn) -> Iterable[FacultyEntity]:
        query = self._build_subject_query(filters)
        qs = FacultyModel.objects.filter(query)[
            pagination.offset:pagination.offset + pagination.limit
        ]
        return [faculty.to_entity() for faculty in qs]

    def get_faculty_count(self, filters: SearchFilterEntity) -> int:
        query = self._build_subject_query(filters)

        return FacultyModel.objects.filter(query).count()

    def get_faculty_by_uuid(self, faculty_uuid: str) -> FacultyEntity:
        try:
            faculty = FacultyModel.objects.get(faculty_uuid=faculty_uuid)
        except FacultyModel.DoesNotExist:
            raise FacultyUuidNotFoundException(uuid=faculty_uuid)

        return faculty.to_entity()
