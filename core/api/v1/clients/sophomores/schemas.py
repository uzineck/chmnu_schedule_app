from ninja import Schema

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity


class SophomoreSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str
    email: str


class SignUpInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str
    email: str
    password: str


class LogInSchema(Schema):
    email: str
    password: str


class TokenOutSchema(SophomoreSchema):
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
