from ninja import Schema

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity


class SignUpInSchema(Schema):
    first_name: str
    last_name: str
    middle_name: str
    email: str
    password: str


class SignUpOutSchema(Schema):
    sophomore: SophomoreEntity


class LogInSchema(Schema):
    email: str
    password: str


class LogInOutSchema(Schema):
    token: str




