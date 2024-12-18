from dataclasses import dataclass

from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.services.timeslot import BaseTimeslotService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class GetOrCreateLessonUseCase:
    lesson_service: BaseLessonService
    subject_service: BaseSubjectService
    teacher_service: BaseTeacherService
    room_service: BaseRoomService
    timeslot_service: BaseTimeslotService

    uuid_validator_service: BaseUuidValidatorService

    def execute(
        self,
        lesson: LessonEntity,
        subject_uuid: str,
        teacher_uuid: str,
        room_uuid: str,
    ) -> LessonEntity:

        self.uuid_validator_service.validate(uuid_list=[subject_uuid, teacher_uuid, room_uuid])

        subject = self.subject_service.get_by_uuid(subject_uuid=subject_uuid)
        teacher = self.teacher_service.get_by_uuid(teacher_uuid=teacher_uuid)
        room = self.room_service.get_by_uuid(room_uuid=room_uuid)
        timeslot = self.timeslot_service.get_or_create(
            day=lesson.timeslot.day,
            ord_number=lesson.timeslot.ord_number,
            is_even=lesson.timeslot.is_even,
        )

        lesson_entity = LessonEntity(
            type=lesson.type,
            subject=subject,
            teacher=teacher,
            room=room,
            timeslot=timeslot,
        )

        if self.lesson_service.check_exists(lesson=lesson_entity):
            lesson = self.lesson_service.get_by_lesson_entity(lesson=lesson_entity)
            return lesson

        saved_lesson = self.lesson_service.save(lesson=lesson_entity)
        return saved_lesson
