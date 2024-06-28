from django.db.models import Q

from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.exceptions.groups import GroupNotFoundException
from core.apps.schedule.exceptions.lesson import LessonNotFoundException
from core.apps.schedule.filters.group import GroupFilter
from core.apps.schedule.models import Lesson as LessonModel
from core.apps.schedule.models.groups import Group as GroupModel


class BaseGroupService(ABC):
    @abstractmethod
    def get_or_create(
        self,
        group_number: str,
        has_subgroups: bool,
        sophomore_id: int,
    ) -> GroupEntity:
        ...

    @abstractmethod
    def get_group_by_number(self, group_number: str) -> GroupEntity:
        ...

    @abstractmethod
    def get_all_groups(self) -> Iterable[GroupEntity]:
        ...

    @abstractmethod
    def get_group_lessons(self, group_number: str, filters: GroupFilter) -> Iterable[LessonEntity]:
        ...

    @abstractmethod
    def add_lesson(self, group_number: str, lesson_id: int) -> GroupEntity:
        ...

    @abstractmethod
    def remove_lesson(self, group_number: str, lesson_id: int) -> GroupEntity:
        ...


class ORMGroupService(BaseGroupService):

    def _build_lesson_query(self, filters: GroupFilter) -> Q:
        query = Q()
        print(filters)

        if filters.subgroup is not None:
            print(filters.subgroup)
            query &= Q(subgroup=filters.subgroup)
            print(query)
        if filters.is_even is not None:
            print(filters.is_even)
            query &= Q(timeslot__is_even=filters.is_even)
            print(query)

        return query

    def get_or_create(
        self,
        group_number: str,
        has_subgroups: bool,
        sophomore_id: int,
    ) -> GroupEntity:
        group, _ = GroupModel.objects.get_or_create(
            number=group_number,
            has_subgroups=has_subgroups,
            sophomore_id=sophomore_id,
        )

        return group.to_entity()

    def get_group_by_number(self, group_number: str) -> GroupEntity:
        try:
            group = GroupModel.objects.get(number=group_number)
        except GroupModel.DoesNotExist:
            raise GroupNotFoundException(group_number=group_number)

        return group.to_entity()

    def get_group_lessons(self, group_number: str, filters: GroupFilter) -> Iterable[LessonEntity]:
        query = self._build_lesson_query(filters)
        qs = LessonModel.objects.filter(Q(group_lessons__number=group_number) & query)

        return [lesson.to_entity() for lesson in qs]

    def get_all_groups(self) -> Iterable[GroupEntity]:
        groups = GroupModel.objects.all()

        for group in groups:
            yield group.to_entity()

    def add_lesson(self, group_number: str, lesson_id: int) -> GroupEntity:
        try:
            group = GroupModel.objects.get(number=group_number)
        except GroupModel.DoesNotExist:
            raise GroupNotFoundException(group_number=group_number)

        try:
            lesson = LessonModel.objects.get(id=lesson_id)
        except LessonModel.DoesNotExist:
            raise LessonNotFoundException(lesson_id=lesson_id)

        group.lessons.add(lesson)

        return group.to_entity()

    def remove_lesson(self, group_number: str, lesson_id: int) -> GroupEntity:
        try:
            group = GroupModel.objects.get(number=group_number)
        except GroupModel.DoesNotExist:
            raise GroupNotFoundException(group_number=group_number)

        try:
            lesson = LessonModel.objects.get(id=lesson_id)
        except LessonModel.DoesNotExist:
            raise LessonNotFoundException(lesson_id=lesson_id)

        group.lessons.remove(lesson)

        return group.to_entity()
