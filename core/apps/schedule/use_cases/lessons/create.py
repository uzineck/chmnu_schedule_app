from dataclasses import dataclass

from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.services.timeslot import BaseTimeslotService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class CreateLessonUseCase:
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
        timeslot_id: int,
    ) -> LessonEntity:

        self.uuid_validator_service.validate(uuid_list=[subject_uuid, teacher_uuid, room_uuid])

        subject = self.subject_service.get_subject_by_uuid(subject_uuid=subject_uuid)
        teacher = self.teacher_service.get_teacher_by_uuid(teacher_uuid=teacher_uuid)
        room = self.room_service.get_room_by_uuid(room_uuid=room_uuid)
        timeslot = self.timeslot_service.get_timeslot_by_id(timeslot_id=timeslot_id)

        lesson_entity = LessonEntity(
            type=lesson.type,
            subject=subject,
            teacher=teacher,
            room=room,
            timeslot=timeslot,
        )

        existing_lesson: bool = self.lesson_service.check_lesson_exists(lesson=lesson_entity)

        if existing_lesson:
            lesson = self.lesson_service.get_lessons_by_lesson_entity(lesson=lesson_entity)
            return lesson

        saved_lesson = self.lesson_service.save_lesson(lesson=lesson_entity)
        return saved_lesson
