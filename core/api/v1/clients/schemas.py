from ninja import Schema

from core.apps.common.models import ClientRole


class ClientSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str
    role: ClientRole
    email: str


class SignUpInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str
    role: ClientRole
    email: str
    password: str


class LogInSchema(Schema):
    email: str
    password: str


class TokenOutSchema(ClientSchema):
    token: str


class UpdatePwInSchema(Schema):
    old_password: str
    new_password: str


class UpdateEmailInSchema(Schema):
    email: str
    password: str


class UpdateCredentialsInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str


class UpdateRoleInSchema(Schema):
    email: str
    role: ClientRole


class UpdateGroupHeadmanSchema(Schema):
    group_number: str
    headman_email: str
