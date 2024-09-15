import punq

from core.project.containers.services.schedule.group import register_group_services
from core.project.containers.services.schedule.group_lesson import register_group_lesson_services
from core.project.containers.services.schedule.lesson import register_lesson_services
from core.project.containers.services.schedule.room import register_room_services
from core.project.containers.services.schedule.subject import register_subject_services
from core.project.containers.services.schedule.teacher import register_teacher_services
from core.project.containers.services.schedule.timeslot import register_timeslot_services


def register_schedule_services(container: punq.Container):
    register_group_services(container=container)
    register_lesson_services(container=container)
    register_group_lesson_services(container=container)
    register_teacher_services(container=container)
    register_subject_services(container=container)
    register_room_services(container=container)
    register_timeslot_services(container=container)
