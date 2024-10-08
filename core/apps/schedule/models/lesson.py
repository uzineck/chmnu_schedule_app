from django.db import models

import uuid

from core.apps.common.models import (
    LessonType,
    TimedBaseModel,
)
from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.models.room import Room
from core.apps.schedule.models.subject import Subject
from core.apps.schedule.models.teacher import Teacher
from core.apps.schedule.models.timeslot import Timeslot


class Lesson(TimedBaseModel):
    lesson_uuid = models.UUIDField(
        verbose_name='UUID lesson representation',
        editable=False,
        default=uuid.uuid4,
    )
    type = models.CharField(
        verbose_name="Type of the lesson",
        choices=LessonType,
        max_length=10,
    )
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

    def to_entity(self) -> LessonEntity:
        return LessonEntity(
            id=self.id,
            uuid=str(self.lesson_uuid),
            type=self.type,
            subject=self.subject.to_entity(),
            teacher=self.teacher.to_entity(),
            room=self.room.to_entity(),
            timeslot=self.timeslot.to_entity(),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, lesson: LessonEntity) -> 'Lesson':
        return cls(
            id=lesson.id,
            lesson_uuid=lesson.uuid,
            subject_id=lesson.subject.id,
            teacher_id=lesson.teacher.id,
            timeslot_id=lesson.timeslot.id,
            room_id=lesson.room.id,
            type=lesson.type,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )

    def __str__(self):
        return (
            f"Lesson: {self.type} {self.subject}, "
            f"Teacher: {self.teacher}, "
            f"Day: {self.timeslot.day}, "
            f"Number: {self.timeslot.ord_number}, "
            f"Is_even: {self.timeslot.is_even}"
        )

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        indexes = [
            models.Index(fields=["lesson_uuid"]),
        ]
