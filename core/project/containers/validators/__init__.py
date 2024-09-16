import punq

from .email import register_email_validators
from .group import register_group_validators
from .password import register_password_validators
from .uuid_validator import register_uuid_validators


def register_validators(container: punq.Container):
    register_password_validators(container=container)
    register_email_validators(container=container)
    register_group_validators(container=container)
    register_uuid_validators(container=container)
