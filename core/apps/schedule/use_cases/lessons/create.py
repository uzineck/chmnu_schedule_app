from dataclasses import dataclass

from core.apps.schedule.entities.lesson import Lesson as LessonEntity
from core.apps.schedule.services.lessons import BaseLessonService
from core.apps.schedule.services.rooms import BaseRoomService
from core.apps.schedule.services.subjects import BaseSubjectService
from core.apps.schedule.services.teachers import BaseTeacherService
from core.apps.schedule.services.timeslots import BaseTimeslotService


@dataclass
class CreateLessonUseCase:
    lesson_service: BaseLessonService
    subject_service: BaseSubjectService
    teacher_service: BaseTeacherService
    room_service: BaseRoomService
    timeslot_service: BaseTimeslotService

    def execute(self,
                lesson: LessonEntity,
                subject_id: int,
                teacher_id: int,
                room_id: int,
                timeslot_id: id) -> LessonEntity:

        subject = self.subject_service.get_subject_by_id(subject_id=subject_id)
        teacher = self.teacher_service.get_teacher_by_id(teacher_id=teacher_id)
        room = self.room_service.get_room_by_id(room_id=room_id)
        timeslot = self.timeslot_service.get_timeslot_by_id(timeslot_id=timeslot_id)

        lesson_entity = LessonEntity(subject=subject,
                                     teacher=teacher,
                                     room=room,
                                     timeslot=timeslot,
                                     type=lesson.type,
                                     subgroup=lesson.subgroup)
        print(lesson_entity)

        saved_lesson = self.lesson_service.save_lesson(lesson=lesson_entity)

        return saved_lesson

