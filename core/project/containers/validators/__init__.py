import punq

from .email import register_email_validators
from .faculty import register_faculty_validators
from .group import register_group_validators
from .password import register_password_validators
from .room import register_room_validators
from .subject import register_subject_validators
from .teacher import register_teacher_validators
from .uuid_validator import register_uuid_validators


def register_validators(container: punq.Container):
    register_password_validators(container=container)
    register_email_validators(container=container)
    register_group_validators(container=container)
    register_uuid_validators(container=container)
    register_room_validators(container=container)
    register_subject_validators(container=container)
    register_teacher_validators(container=container)
    register_faculty_validators(container=container)
