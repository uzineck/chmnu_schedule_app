from ninja import Schema

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.common.models import ClientRole


class ClientSchemaPublic(Schema):
    last_name: str
    first_name: str
    middle_name: str

    @classmethod
    def from_entity(cls, client: ClientEntity) -> 'ClientSchemaPublic':
        return cls(
            last_name=client.last_name,
            first_name=client.first_name,
            middle_name=client.middle_name,
        )


class ClientSchemaPrivate(Schema):
    last_name: str
    first_name: str
    middle_name: str
    roles: list[ClientRole]
    email: str

    @classmethod
    def from_entity(cls, client: ClientEntity) -> 'ClientSchemaPrivate':
        return cls(
            last_name=client.last_name,
            first_name=client.first_name,
            middle_name=client.middle_name,
            roles=client.roles,
            email=client.email,
        )


class SignUpInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str
    roles: list[ClientRole]
    email: str
    password: str
    verify_password: str


class LogInSchema(Schema):
    email: str
    password: str


class TokenClientOutSchema(ClientSchemaPrivate):
    access_token: str
    refresh_token: str | None = None

    @classmethod
    def from_entity_with_tokens(cls, client: ClientEntity, tokens: TokenEntity) -> 'TokenClientOutSchema':
        return cls(
            last_name=client.last_name,
            first_name=client.first_name,
            middle_name=client.middle_name,
            roles=client.roles,
            email=client.email,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    @classmethod
    def from_entity_with_token_values(
            cls,
            client: ClientEntity,
            access_token: str,
            refresh_token: str | None = None,
    ) -> 'TokenClientOutSchema':
        return cls(
            last_name=client.last_name,
            first_name=client.first_name,
            middle_name=client.middle_name,
            roles=client.roles,
            email=client.email,
            access_token=access_token,
            refresh_token=refresh_token,
        )


class TokenOutSchema(Schema):
    access_token: str
    refresh_token: str | None = None

    @classmethod
    def from_entity(cls, tokens_entity: TokenEntity) -> 'TokenOutSchema':
        return cls(
            access_token=tokens_entity.access_token,
            refresh_token=tokens_entity.refresh_token,
        )

    @classmethod
    def from_values(cls, access_token: str, refresh_token: str | None = None) -> 'TokenOutSchema':
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
        )


class TokenInSchema(Schema):
    token: str


class UpdatePwInSchema(Schema):
    old_password: str
    new_password: str
    verify_password: str


class UpdatePwInAdminSchema(Schema):
    new_password: str
    verify_password: str


class UpdateEmailInSchema(Schema):
    client_email: str
    new_email: str
    password: str


class CredentialsInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str


class RolesInSchema(Schema):
    roles: list[ClientRole]
