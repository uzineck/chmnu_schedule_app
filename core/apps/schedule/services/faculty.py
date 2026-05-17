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
    FacultyAlreadyExistsException,
    FacultyDeleteException,
    FacultyNotFoundException,
    FacultyUpdateException,
)
from core.apps.schedule.models import Faculty as FacultyModel


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
    def check_exists_by_name(self, faculty_name: str) -> bool:
        ...

    @abstractmethod
    def check_exists_by_code_name(self, faculty_code_name: str) -> bool:
        ...

    @abstractmethod
    def find_any_by_code_name(self, faculty_code_name: str) -> FacultyEntity | None:
        ...

    @abstractmethod
    def update_name(self, faculty_id: int, new_name: str) -> None:
        ...

    @abstractmethod
    def update_code_name(self, faculty_id: int, new_code_name: str) -> None:
        ...

    @abstractmethod
    def soft_delete(self, faculty_id: int) -> None:
        ...

    @abstractmethod
    def restore(self, faculty_id: int) -> None:
        ...


class ORMFacultyService(BaseFacultyService):
    def _build_faculty_query(self, filters: SearchFilterEntity) -> Q:
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
            raise FacultyAlreadyExistsException(code_name=code_name, name=name)

        return faculty.to_entity()

    def get_all(self) -> list[FacultyEntity]:
        return [faculty.to_entity() for faculty in FacultyModel.objects.all()]

    def get_list(self, filters: SearchFilterEntity, pagination: PaginationIn) -> list[FacultyEntity]:
        query = self._build_faculty_query(filters)
        qs = FacultyModel.objects.filter(query)[
            pagination.offset:pagination.offset + pagination.limit
        ]
        return [faculty.to_entity() for faculty in qs]

    def get_count(self, filters: SearchFilterEntity) -> int:
        query = self._build_faculty_query(filters)

        return FacultyModel.objects.filter(query).count()

    def get_by_uuid(self, faculty_uuid: str) -> FacultyEntity:
        try:
            faculty = FacultyModel.objects.get(faculty_uuid=faculty_uuid)
        except FacultyModel.DoesNotExist:
            raise FacultyNotFoundException(uuid=faculty_uuid)

        return faculty.to_entity()

    def get_by_id(self, faculty_id: int) -> FacultyEntity:
        try:
            faculty = FacultyModel.objects.get(id=faculty_id)
        except FacultyModel.DoesNotExist:
            raise FacultyNotFoundException(id=faculty_id)

        return faculty.to_entity()

    def check_exists_by_name(self, faculty_name: str) -> bool:
        return FacultyModel.objects.filter(name=faculty_name).exists()

    def check_exists_by_code_name(self, faculty_code_name: str) -> bool:
        return FacultyModel.objects.filter(code_name=faculty_code_name).exists()

    def find_any_by_code_name(self, faculty_code_name: str) -> FacultyEntity | None:
        faculty = FacultyModel.all_objects.filter(code_name=faculty_code_name).first()
        return faculty.to_entity() if faculty is not None else None

    def update_name(self, faculty_id: int, new_name: str) -> None:
        is_updated = FacultyModel.objects.filter(id=faculty_id).update(name=new_name)

        if not is_updated:
            raise FacultyUpdateException(id=faculty_id)

    def update_code_name(self, faculty_id: int, new_code_name: str) -> None:
        is_updated = FacultyModel.objects.filter(id=faculty_id).update(code_name=new_code_name)

        if not is_updated:
            raise FacultyUpdateException(id=faculty_id)

    def soft_delete(self, faculty_id: int) -> None:
        is_updated = FacultyModel.objects.filter(id=faculty_id).update(is_active=False)

        if not is_updated:
            raise FacultyDeleteException(id=faculty_id)

    def restore(self, faculty_id: int) -> None:
        FacultyModel.all_objects.filter(id=faculty_id).update(is_active=True)
