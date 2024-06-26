from django.db import models

from core.apps.common.models import (
    LessonType,
    Subgroup,
    TimedBaseModel,
)
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.models.rooms import Room
from core.apps.schedule.models.subjects import Subject
from core.apps.schedule.models.teachers import Teacher
from core.apps.schedule.models.timeslots import Timeslot


class Lesson(TimedBaseModel):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        verbose_name="Subject of the lesson",
        related_name='lesson_subject',
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        verbose_name="Teacher that holds the lesson",
        related_name="lesson_teacher",
    )
    type = models.CharField(
        verbose_name="Type of the lesson",
        choices=LessonType,
        max_length=10,
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        verbose_name="Room where the lesson is held",
        related_name='lesson_room',
    )
    timeslot = models.ForeignKey(
        Timeslot,
        on_delete=models.PROTECT,
        verbose_name="Timeslot when the lesson is held",
        related_name='lesson_timeslot',
    )
    subgroup = models.CharField(
        max_length=1,
        choices=Subgroup,
        null=True,
    )

    def to_entity(self) -> LessonEntity:
        return LessonEntity(
            id=self.id,
            subject=self.subject,
            teacher=self.teacher,
            room=self.room,
            timeslot=self.timeslot,
            type=self.type,
            subgroup=self.subgroup,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, lesson: LessonEntity) -> 'Lesson':
        return cls(
            id=lesson.id,
            subject_id=lesson.subject.id,
            teacher_id=lesson.teacher.id,
            timeslot_id=lesson.timeslot.id,
            room_id=lesson.room.id,
            type=lesson.type,
            subgroup=lesson.subgroup,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )

    def __str__(self):
        return (
            f"Lesson: {self.type} {self.subject}, "
            f"Teacher: {self.teacher}, "
            f"Day: {self.timeslot.day}, "
            f"Number: {self.timeslot.ord_number}, "
            f"Subgroup: {self.subgroup}"
        )

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
