from django.db.models import Q

from abc import (
    ABC,
    abstractmethod,
)

from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.entities.views import (
    GroupForLessonView,
    LessonForGroupView,
    LessonWithGroupsView,
)
from core.apps.schedule.exceptions.lesson import (
    LessonDeleteError,
    LessonNotFoundException,
)
from core.apps.schedule.filters.group import LessonFilter
from core.apps.schedule.models import Lesson as LessonModel
from core.apps.schedule.models.group import GroupLesson as GroupLessonModel


class BaseLessonService(ABC):
    @abstractmethod
    def get_or_create(self, lesson: LessonEntity) -> LessonEntity:
        ...

    @abstractmethod
    def get_by_uuid(self, lesson_uuid: str) -> LessonEntity:
        ...

    @abstractmethod
    def get_lessons_with_groups(self, lesson_filter: Q) -> list[LessonWithGroupsView]:
        ...

    @abstractmethod
    def get_lessons_with_subgroups_for_group(
            self,
            group_id: int,
            filter_query: LessonFilter,
    ) -> list[LessonForGroupView]:
        ...

    @abstractmethod
    def get_lessons_with_groups_for_teacher(
            self,
            teacher_id: int,
            filter_query: LessonFilter,
    ) -> list[LessonWithGroupsView]:
        ...

    @abstractmethod
    def check_if_teacher_has_lessons(self, teacher_id: int) -> bool:
        ...

    @abstractmethod
    def check_if_subject_has_lessons(self, subject_id: int) -> bool:
        ...

    @abstractmethod
    def check_if_room_has_lessons(self, room_id: int) -> bool:
        ...

    @abstractmethod
    def delete_by_uuid(self, lesson_uuid: str) -> None:
        ...


class ORMLessonService(BaseLessonService):

    def get_or_create(self, lesson: LessonEntity) -> LessonEntity:
        lesson_model, _ = LessonModel.objects.get_or_create(
            subject_id=lesson.subject.id,
            teacher_id=lesson.teacher.id,
            room_id=lesson.room.id,
            timeslot_id=lesson.timeslot.id,
            type=lesson.type,
        )
        return lesson_model.to_entity()

    def get_by_uuid(self, lesson_uuid: str) -> LessonEntity:
        try:
            lesson = (
                LessonModel.objects.
                select_related("subject", "teacher", "room", "timeslot").
                get(lesson_uuid=lesson_uuid)
            )
        except LessonModel.DoesNotExist:
            raise LessonNotFoundException(uuid=lesson_uuid)

        return lesson.to_entity()

    def _build_group_lesson_filter(self, filters: LessonFilter) -> Q:
        query = Q()
        if filters.subgroup is not None:
            query &= Q(subgroup=filters.subgroup)
        if filters.is_even is not None:
            query &= Q(lesson__timeslot__is_even=filters.is_even)
        return query

    def get_lessons_with_groups(self, lesson_filter: Q) -> list[LessonWithGroupsView]:
        rows = (
            GroupLessonModel.objects
            .filter(lesson_filter)
            .select_related(
                'lesson__subject', 'lesson__teacher', 'lesson__room', 'lesson__timeslot',
                'group__faculty', 'group__headman',
            )
            .prefetch_related('group__headman__roles')
            .order_by('lesson__timeslot__day', 'lesson__timeslot__ord_number', 'group__number')
        )

        lesson_bucket: dict[int, LessonWithGroupsView] = {}
        group_bucket: dict[tuple[int, int], GroupForLessonView] = {}

        for row in rows:
            if row.lesson_id not in lesson_bucket:
                lesson_bucket[row.lesson_id] = LessonWithGroupsView(
                    lesson=row.lesson.to_entity(),
                    groups=[],
                )
            key = (row.lesson_id, row.group_id)
            if key not in group_bucket:
                gv = GroupForLessonView(group=row.group.to_entity(), subgroups=[])
                group_bucket[key] = gv
                lesson_bucket[row.lesson_id].groups.append(gv)
            if row.subgroup is not None:
                group_bucket[key].subgroups.append(row.subgroup)

        return list(lesson_bucket.values())

    def get_lessons_with_groups_for_teacher(
            self,
            teacher_id: int,
            filter_query: LessonFilter,
    ) -> list[LessonWithGroupsView]:
        query = self._build_group_lesson_filter(filter_query) & Q(lesson__teacher_id=teacher_id)
        return self.get_lessons_with_groups(query)

    def get_lessons_with_subgroups_for_group(
            self,
            group_id: int,
            filter_query: LessonFilter,
    ) -> list[LessonForGroupView]:
        query = self._build_group_lesson_filter(filter_query) & Q(group_id=group_id)
        rows = (
            GroupLessonModel.objects
            .filter(query)
            .select_related('lesson__subject', 'lesson__teacher', 'lesson__room', 'lesson__timeslot')
            .order_by('lesson__timeslot__day', 'lesson__timeslot__ord_number')
        )

        bucket: dict[int, LessonForGroupView] = {}
        for row in rows:
            if row.lesson_id not in bucket:
                bucket[row.lesson_id] = LessonForGroupView(
                    lesson=row.lesson.to_entity(),
                    subgroups=[],
                )
            if row.subgroup is not None:
                bucket[row.lesson_id].subgroups.append(row.subgroup)

        return list(bucket.values())

    def check_if_teacher_has_lessons(self, teacher_id: int) -> bool:
        return GroupLessonModel.objects.filter(lesson__teacher_id=teacher_id).exists()

    def check_if_subject_has_lessons(self, subject_id: int) -> bool:
        return GroupLessonModel.objects.filter(lesson__subject_id=subject_id).exists()

    def check_if_room_has_lessons(self, room_id: int) -> bool:
        return GroupLessonModel.objects.filter(lesson__room_id=room_id).exists()

    def delete_by_uuid(self, lesson_uuid: str) -> None:
        is_deleted, _ = LessonModel.objects.filter(
            lesson_uuid=lesson_uuid,
        ).delete()

        if not is_deleted:
            raise LessonDeleteError(uuid=lesson_uuid)
