from abc import ABC, abstractmethod
from typing import Iterable

from pytils.translit import slugify
from django.db.models import Q
from django.db import IntegrityError

from core.api.filters import PaginationIn
from core.apps.schedule.exceptions.subject import SubjectNotFoundException, SubjectAlreadyExistException
from core.apps.common.filters import SearchFilter as SearchFiltersEntity
from core.apps.schedule.models import Subject as SubjectModel
from core.apps.schedule.entities.subject import Subject as SubjectEntity


class BaseSubjectService(ABC):
    @abstractmethod
    def get_or_create(self, title: str) -> SubjectEntity:
        ...

    @abstractmethod
    def get_subject_list(self, filters: SearchFiltersEntity,  pagination: PaginationIn) -> Iterable[SubjectEntity]:
        ...

    @abstractmethod
    def get_subject_count(self, filters: SearchFiltersEntity) -> int:
        ...

    @abstractmethod
    def get_subject_by_id(self, subject_id: int) -> SubjectEntity:
        ...

    @abstractmethod
    def update_subject_by_id(self, subject_id: int, title: str) -> SubjectEntity:
        ...

    @abstractmethod
    def delete_subject_by_id(self, subject_id: int) -> None:
        ...



class ORMSubjectService(BaseSubjectService):

    def _build_subject_query(self, filters: SearchFiltersEntity) -> Q:
        query = Q()

        if filters.search is not None:
            query &= Q(title__icontains=filters.search) | Q(slug__icontains=filters.search)

        return query

    def get_or_create(self, title: str) -> SubjectEntity:
        try:
            slug = slugify(title.strip())
            subject, _ = SubjectModel.objects.get_or_create(title=title.strip(), slug=slug)
        except IntegrityError:
            raise SubjectAlreadyExistException(title=title)
        return subject.to_entity()

    def get_subject_list(self, filters: SearchFiltersEntity, pagination: PaginationIn) -> Iterable[SubjectEntity]:
        query = self._build_subject_query(filters)
        qs = SubjectModel.objects.filter(query)[
            pagination.offset:pagination.offset + pagination.limit
        ]
        return [subject.to_entity() for subject in qs]

    def get_subject_count(self, filters: SearchFiltersEntity) -> int:
        query = self._build_subject_query(filters)

        return SubjectModel.objects.filter(query).count()

    def get_subject_by_id(self, subject_id: int) -> SubjectEntity:
        try:
            subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            raise SubjectNotFoundException(subject_info=str(subject_id))
        return subject.to_entity()

    def update_subject_by_id(self, subject_id: int, title: str) -> SubjectEntity:
        try:
            slug = slugify(title.strip())
            SubjectModel.objects.filter(id=subject_id).update(title=title.strip(), slug=slug)
        except IntegrityError:
            raise SubjectAlreadyExistException(title=title)
        try:
            updated_subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            raise SubjectNotFoundException(subject_info=str(subject_id))
        return updated_subject.to_entity()

    def delete_subject_by_id(self, subject_id: int) -> None:
        try:
            subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            raise SubjectNotFoundException(subject_info=str(subject_id))

        subject.delete()


