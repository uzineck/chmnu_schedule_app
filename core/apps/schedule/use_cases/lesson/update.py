from dataclasses import dataclass

from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.services.timeslot import BaseTimeslotService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class UpdateLessonUseCase:
    lesson_service: BaseLessonService
    subject_service: BaseSubjectService
    teacher_service: BaseTeacherService
    room_service: BaseRoomService
    timeslot_service: BaseTimeslotService

    uuid_validator_service: BaseUuidValidatorService

    def execute(
        self,
        lesson_uuid: str,
        lesson: LessonEntity,
        subject_uuid: str,
        teacher_uuid: str,
        room_uuid: str,
    ) -> tuple[LessonEntity, LessonEntity]:

        self.uuid_validator_service.validate(uuid_list=[lesson_uuid, subject_uuid, teacher_uuid, room_uuid])

        old_lesson = self.lesson_service.get_by_uuid(lesson_uuid=lesson_uuid)

        lesson_type = old_lesson.type
        subject = old_lesson.subject
        teacher = old_lesson.teacher
        room = old_lesson.room
        timeslot = old_lesson.timeslot

        if subject.uuid != subject_uuid:
            subject = self.subject_service.get_by_uuid(subject_uuid=subject_uuid)

        if teacher.uuid != teacher_uuid:
            teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)

        if room.uuid != room_uuid:
            room = self.room_service.get_by_uuid(room_uuid=room_uuid)

        if timeslot != lesson.timeslot:
            timeslot = self.timeslot_service.get_or_create(
                day=lesson.timeslot.day,
                ord_number=lesson.timeslot.ord_number,
                is_even=lesson.timeslot.is_even,
            )

        if lesson_type != lesson.type:
            lesson_type = lesson.type

        lesson_entity = LessonEntity(
            type=lesson_type,
            subject=subject,
            teacher=teacher,
            room=room,
            timeslot=timeslot,
        )

        if self.lesson_service.check_exists(lesson=lesson_entity):
            lesson = self.lesson_service.get_by_lesson_entity(lesson=lesson_entity)
            return lesson, old_lesson

        saved_lesson = self.lesson_service.save(lesson=lesson_entity)
        return saved_lesson, old_lesson
