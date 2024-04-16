from ninja import Schema

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity


class SignUpInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str
    email: str
    password: str


class SignUpOutSchema(Schema):
    greetings: str


class LogInSchema(Schema):
    email: str
    password: str


class LogInOutSchema(Schema):
    token: str


class UpdatePwInSchema(Schema):
    old_password: str
    new_password: str


class UpdatePwOutSchema(Schema):
    status: str


class UpdateEmailInSchema(Schema):
    email: str
    password: str


class UpdateEmailOutSchema(Schema):
    email: str
    token: str


class UpdateCredentialsInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str


class UpdateCredentialsOutSchema(Schema):
    sophomore: str
