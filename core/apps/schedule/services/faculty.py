from django.db import IntegrityError
from django.db.models import Q

import logging
from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter as SearchFilterEntity
from core.apps.schedule.entities.faculty import Faculty as FacultyEntity
from core.apps.schedule.exceptions.faculty import (
    FacultyAlreadyExistsException,
    FacultyDeleteException,
    FacultyNotFoundException,
    FacultyUpdateException,
)
from core.apps.schedule.models import Faculty as FacultyModel


logger = logging.getLogger(__name__)


class BaseFacultyService(ABC):
    @abstractmethod
    def create(self, name: str, code_name: str) -> FacultyEntity:
        ...

    @abstractmethod
    def get_all(self) -> Iterable[FacultyEntity]:
        ...

    @abstractmethod
    def get_list(self, filters: SearchFilterEntity, pagination: PaginationIn) -> Iterable[FacultyEntity]:
        ...

    @abstractmethod
    def get_count(self, filters: SearchFilterEntity) -> int:
        ...

    @abstractmethod
    def get_by_uuid(self, faculty_uuid: str) -> FacultyEntity:
        ...

    @abstractmethod
    def get_by_id(self, faculty_id: int) -> FacultyEntity:
        ...

    @abstractmethod
    def update_name(self, faculty_id: int, new_name: str) -> None:
        ...

    @abstractmethod
    def update_code_name(self, faculty_id: int, new_code_name: str) -> None:
        ...

    @abstractmethod
    def delete(self, faculty_id: int) -> None:
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
            logger.error(f"Faculty Creation Error ({name=}, {code_name=})")
            raise FacultyAlreadyExistsException(code_name=code_name, name=name)

        return faculty.to_entity()

    def get_all(self) -> Iterable[FacultyEntity]:
        faculties = FacultyModel.objects.all()

        for faculty in faculties:
            yield faculty.to_entity()

    def get_list(self, filters: SearchFilterEntity, pagination: PaginationIn) -> Iterable[FacultyEntity]:
        query = self._build_subject_query(filters)
        qs = FacultyModel.objects.filter(query)[
            pagination.offset:pagination.offset + pagination.limit
        ]
        return [faculty.to_entity() for faculty in qs]

    def get_count(self, filters: SearchFilterEntity) -> int:
        query = self._build_subject_query(filters)

        return FacultyModel.objects.filter(query).count()

    def get_by_uuid(self, faculty_uuid: str) -> FacultyEntity:
        try:
            faculty = FacultyModel.objects.get(faculty_uuid=faculty_uuid)
        except FacultyModel.DoesNotExist:
            logger.error(f"Faculty Does Not Exist Error ({faculty_uuid=})")
            raise FacultyNotFoundException(uuid=faculty_uuid)

        return faculty.to_entity()

    def get_by_id(self, faculty_id: int) -> FacultyEntity:
        try:
            faculty = FacultyModel.objects.get(id=faculty_id)
        except FacultyModel.DoesNotExist:
            logger.error(f"Faculty Does Not Exist Error ({faculty_id=})")
            raise FacultyNotFoundException(id=faculty_id)

        return faculty.to_entity()

    def update_name(self, faculty_id: int, new_name: str) -> None:
        is_updated = FacultyModel.objects.filter(id=faculty_id).update(name=new_name)

        if not is_updated:
            logger.error(f"Faculty Update Name Error ({faculty_id=}, {new_name=})")
            raise FacultyUpdateException(id=faculty_id)

    def update_code_name(self, faculty_id: int, new_code_name: str) -> None:
        is_updated = FacultyModel.objects.filter(id=faculty_id).update(code_name=new_code_name)

        if not is_updated:
            logger.error(f"Faculty Update Code Name Error ({faculty_id=}, {new_code_name=})")
            raise FacultyUpdateException(id=faculty_id)

    def delete(self, faculty_id: int) -> None:
        is_deleted = FacultyModel.objects.filter(id=faculty_id).delete()

        if not is_deleted:
            logger.error(f"Faculty Delete Error ({faculty_id=})")
            raise FacultyDeleteException(id=faculty_id)
