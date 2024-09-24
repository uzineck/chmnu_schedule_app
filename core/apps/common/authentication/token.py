import jwt
from abc import (
    ABC,
    abstractmethod,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from typing import (
    Any,
    ClassVar,
)

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.common.exceptions import JWTKeyParsingException
from core.apps.common.factory import (
    convert_to_timestamp,
    get_new_uuid,
)
from core.apps.common.models import TokenType
from core.project.settings.main import env


class BaseTokenService(ABC):
    @abstractmethod
    def create_access_token(self, client: ClientEntity, payload: dict[str, Any]) -> str:
        ...

    @abstractmethod
    def create_refresh_token(self, client: ClientEntity, payload: dict[str, Any]) -> str:
        ...

    @abstractmethod
    def get_raw_jwt(self, token: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_client_email_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_client_role_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_token_type_from_token(self, token: str) -> TokenType:
        ...

    @abstractmethod
    def get_jti_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_device_id_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_expiration_time_from_token(self, token: str) -> int:
        ...


class JWTTokenService(BaseTokenService):
    JWT_SECRET_KEY: ClassVar[str] = env("JWT_SECRET_KEY")
    ALGORITHM: ClassVar[str] = "HS256"
    TOKEN_TYPE: ClassVar[str] = "type"
    ISSUER: ClassVar[str] = "iss"
    SUBJECT: ClassVar[str] = "sub"
    AUDIENCE: ClassVar[str] = "aud"
    JWT_ID: ClassVar[str] = "jti"
    DEVICE_ID: ClassVar[str] = "device_id"
    NOT_BEFORE: ClassVar[str] = "nbf"
    ISSUED_AT: ClassVar[str] = "iat"
    EXPIRATION_TIME: ClassVar[str] = "exp"
    ACCESS_TOKEN_TTL: timedelta = timedelta(seconds=env.int("ACCESS_TOKEN_EXP"))
    REFRESH_TOKEN_TTL: timedelta = timedelta(seconds=env.int("REFRESH_TOKEN_EXP"))
    CLIENT_EMAIL_KEY: ClassVar[str] = "client_email"
    CLIENT_ROLE_KEY: ClassVar[str] = "client_role"

    def __encode_jwt(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload=payload, key=self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)

    def __decode_jwt_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            jwt=token,
            key=self.JWT_SECRET_KEY,
            algorithms=self.ALGORITHM,
            options={"require": ["type", "exp", "iat", "nbf", "jti"]},
        )

    @staticmethod
    def __generate_jti() -> str:
        return get_new_uuid()

    def __sign_jwt_token(
            self,
            token_type: TokenType,
            subject: str,
            payload: dict[str, Any],
            ttl: timedelta = None,
    ) -> str:
        current_timestamp = convert_to_timestamp(datetime.now(tz=timezone.utc))
        data: dict[str, Any] = {
            self.ISSUER: "chmnu@auth_service",
            self.SUBJECT: subject,
            self.TOKEN_TYPE: token_type,
            self.JWT_ID: self.__generate_jti(),
            self.ISSUED_AT: current_timestamp,
            self.NOT_BEFORE: payload[self.NOT_BEFORE] if payload.get(self.NOT_BEFORE) else current_timestamp,
        }
        data.update({self.EXPIRATION_TIME: data[self.NOT_BEFORE] + int(ttl.total_seconds())}) if ttl else None
        data.update(payload)

        return self.__encode_jwt(payload=data)

    def __get_payload(self, client: ClientEntity, payload: dict[str, Any]) -> dict[str, Any]:
        payload.update({
            self.CLIENT_EMAIL_KEY: client.email,
            self.CLIENT_ROLE_KEY: client.role,
        })

        return payload

    def create_access_token(self, client: ClientEntity, payload: dict[str, Any]) -> str:
        new_payload: dict[str, Any] = self.__get_payload(client=client, payload=payload)
        return self.__sign_jwt_token(
            token_type=TokenType.ACCESS,
            subject=new_payload.get(self.CLIENT_EMAIL_KEY),
            payload=new_payload,
            ttl=self.ACCESS_TOKEN_TTL,
        )

    def create_refresh_token(self, client: ClientEntity, payload: dict[str, Any]) -> str:
        new_payload: dict[str, Any] = self.__get_payload(client=client, payload=payload)
        return self.__sign_jwt_token(
            token_type=TokenType.REFRESH,
            subject=new_payload.get(self.CLIENT_EMAIL_KEY),
            payload=new_payload,
            ttl=self.REFRESH_TOKEN_TTL,
        )

    def get_raw_jwt(self, token: str) -> dict[str, Any]:
        return jwt.decode(jwt=token, options={'verify_signature': False})

    def get_client_email_from_token(self, token: str) -> str:
        payload: dict[str, Any] = self.__decode_jwt_token(token=token)
        user_email: str = payload.get(self.CLIENT_EMAIL_KEY)
        if not user_email:
            raise JWTKeyParsingException
        return user_email

    def get_client_role_from_token(self, token: str) -> str:
        payload: dict[str, Any] = self.__decode_jwt_token(token=token)
        user_role: str = payload.get(self.CLIENT_ROLE_KEY)
        if not user_role:
            raise JWTKeyParsingException
        return user_role

    def get_token_type_from_token(self, token: str) -> TokenType:
        payload: dict[str, Any] = self.__decode_jwt_token(token=token)
        token_type: str = payload.get(self.TOKEN_TYPE)
        if not token_type:
            raise JWTKeyParsingException
        return TokenType(token_type)

    def get_jti_from_token(self, token: str) -> str:
        payload: dict[str, Any] = self.__decode_jwt_token(token=token)
        jti: str = payload.get(self.JWT_ID)
        if not jti:
            raise JWTKeyParsingException
        return jti

    def get_device_id_from_token(self, token: str) -> str:
        payload: dict[str, Any] = self.__decode_jwt_token(token=token)
        device_id: str = payload.get(self.DEVICE_ID)
        if not device_id:
            raise JWTKeyParsingException
        return device_id

    def get_expiration_time_from_token(self, token: str) -> int:
        payload: dict[str, Any] = self.__decode_jwt_token(token=token)
        exp: int = payload.get(self.EXPIRATION_TIME)
        if not exp:
            raise JWTKeyParsingException
        return exp
