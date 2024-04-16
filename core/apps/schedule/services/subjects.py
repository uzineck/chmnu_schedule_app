from abc import ABC, abstractmethod
from dataclasses import dataclass


from pytils.translit import slugify
from django.db.models import Q

from core.apps.schedule.exceptions.subject import SubjectNotFound, SubjectAlreadyExistsException
from core.apps.schedule.filters.subjects import SubjectFilters
from core.apps.schedule.models import Subject as SubjectModel
from core.apps.schedule.entities.subject import Subject as SubjectEntity


class BaseSubjectService(ABC):
    @abstractmethod
    def create(self, title: str) -> SubjectEntity:
        ...

    @abstractmethod
    def get_subject_list(self, subject_title: str) -> list[SubjectEntity]:
        ...

    @abstractmethod
    def get_subject_by_title(self, subject_title: str) -> SubjectEntity:
        ...

    @abstractmethod
    def get_subject_by_id(self, subject_id: str) -> SubjectEntity:
        ...

    @abstractmethod
    def update_subject_by_id(self, subject_id: int, title: str) -> SubjectEntity:
        ...


class SubjectService(BaseSubjectService):

    def _build_subject_query(self, filters: SubjectFilters) -> Q:
        query = Q()

        if filters.search is not None:
            query &= Q(title__icontains=filters.search) | Q(
                slug__icontains=filters.search,
            )

        return query

    def create(self, title: str) -> SubjectEntity:
        from django.db import IntegrityError
        try:
            slug = slugify(title.strip())
            subject: SubjectModel = SubjectModel.objects.create(title=title.strip(), slug=slug)
        except IntegrityError:
            raise SubjectAlreadyExistsException(title=title)
        return subject.to_entity()

    def get_subject_list(self, filters: SubjectFilters) -> list[SubjectEntity]:
        query = self._build_subject_query(filters)
        qs = SubjectModel.objects.filter(query)
        return [subject.to_entity() for subject in qs]

    def get_subject_by_title(self, filters: SubjectFilters) -> SubjectEntity:
        try:
            query = self._build_subject_query(filters)
            qs = SubjectModel.objects.filter(query).first()
            return qs.to_entity()
        except AttributeError:
            raise SubjectNotFound(subject_info=filters.search)

    def get_subject_by_id(self, subject_id: str) -> SubjectEntity:
        try:
            subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            raise SubjectNotFound(subject_info=subject_id)
        return subject.to_entity()

    def update_subject_by_id(self, subject_id: int, title: str) -> SubjectEntity:
        try:
            slug = slugify(title)
            SubjectModel.objects.filter(id=subject_id).update(title=title, slug=slug)
        except IntegrityError:
            raise SubjectAlreadyExistsException(title=title)
        try:
            updated_subject = SubjectModel.objects.get(id=subject_id)
        except SubjectModel.DoesNotExist:
            raise SubjectNotFound(subject_info=str(subject_id))
        return updated_subject.to_entity()

