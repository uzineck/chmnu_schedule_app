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
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.exceptions.subject import (
    SubjectAlreadyExistException,
    SubjectDeleteException,
    SubjectNotFoundException,
    SubjectUpdateException,
)
from core.apps.schedule.models import Subject as SubjectModel


logger = logging.getLogger(__name__)


class BaseSubjectService(ABC):
    @abstractmethod
    def create(self, title: str, slug: str) -> SubjectEntity:
        ...

    @abstractmethod
    def get_all(self) -> Iterable[SubjectEntity]:
        ...

    @abstractmethod
    def get_list(self, filters: SearchFilterEntity, pagination: PaginationIn) -> Iterable[SubjectEntity]:
        ...

    @abstractmethod
    def get_count(self, filters: SearchFilterEntity) -> int:
        ...

    @abstractmethod
    def get_by_uuid(self, subject_uuid: str) -> SubjectEntity:
        ...

    @abstractmethod
    def get_by_id(self, subject_id: int) -> SubjectEntity:
        ...

    @abstractmethod
    def update(self, subject_id: int, title: str, slug: str) -> None:
        ...

    @abstractmethod
    def delete(self, subject_id: int) -> None:
        ...


class ORMSubjectService(BaseSubjectService):
    def _build_subject_query(self, filters: SearchFilterEntity) -> Q:
        query = Q()

        if filters.search is not None:
            query &= Q(title__icontains=filters.search) | Q(slug__icontains=filters.search)

        return query

    def create(self, title: str, slug: str) -> SubjectEntity:
        try:
            subject = SubjectModel.objects.create(title=title, slug=slug)
        except IntegrityError:
            logger.info(f"Subject Creation Error ({title=}, {slug=})")
            raise SubjectAlreadyExistException(title=title)

        return subject.to_entity()

    def get_all(self) -> Iterable[SubjectEntity]:
        subjects = SubjectModel.objects.all()

        for subject in subjects:
            yield subject.to_entity()

    def get_list(self, filters: SearchFilterEntity, pagination: PaginationIn) -> Iterable[SubjectEntity]:
        query = self._build_subject_query(filters)
        qs = SubjectModel.objects.filter(query)[
            pagination.offset:pagination.offset + pagination.limit
        ]
        return [subject.to_entity() for subject in qs]

    def get_count(self, filters: SearchFilterEntity) -> int:
        query = self._build_subject_query(filters)

        return SubjectModel.objects.filter(query).count()

    def get_by_uuid(self, subject_uuid: str) -> SubjectEntity:
        try:
            subject = SubjectModel.objects.get(subject_uuid=subject_uuid)
        except SubjectModel.DoesNotExist:
            logger.error(f"Subject Does Not Exist Error ({subject_uuid=})")
            raise SubjectNotFoundException(uuid=subject_uuid)
        return subject.to_entity()

    def get_by_id(self, subject_id: int) -> SubjectEntity:
        try:
            subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            logger.error(f"Subject Does Not Exist Error ({subject_id=})")
            raise SubjectNotFoundException(id=subject_id)
        return subject.to_entity()

    def update(self, subject_id: int, title: str, slug: str) -> None:
        is_updated = SubjectModel.objects.filter(id=subject_id).update(title=title, slug=slug)

        if not is_updated:
            logger.error(f"Subject Update Description Error ({subject_id=}, {title=}, {slug=})")
            raise SubjectUpdateException(id=subject_id)

    def delete(self, subject_id: int) -> None:
        is_deleted = SubjectModel.objects.filter(id=subject_id).delete()

        if not is_deleted:
            logger.error(f"Subject Delete Error ({subject_id=})")
            raise SubjectDeleteException(id=subject_id)
