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
from core.apps.clients.entities.token import Token as TokenEntity
from core.apps.common.exceptions import JWTKeyParsingException
from core.apps.common.factory import convert_to_timestamp
from core.apps.common.models import TokenType
from core.project.settings.main import env


class BaseTokenService(ABC):
    @abstractmethod
    def create_tokens(self, client: ClientEntity) -> TokenEntity:
        ...

    @abstractmethod
    def validate_token(self, token: str) -> dict[str, Any]:
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


class JWTTokenService(BaseTokenService):
    JWT_SECRET_KEY: ClassVar[str] = env("JWT_SECRET_KEY")
    ALGORITHM: ClassVar[str] = "HS256"
    TOKEN_TYPE: ClassVar[str] = "type"
    ISSUER: ClassVar[str] = "iss"
    SUBJECT: ClassVar[str] = "sub"
    AUDIENCE: ClassVar[str] = "aud"
    NOT_BEFORE: ClassVar[str] = "nbf"
    ISSUED_AT: ClassVar[str] = "iat"
    EXPIRATION_TIME: ClassVar[str] = "exp"
    ACCESS_TOKEN_TTL: timedelta = timedelta(seconds=env.int("ACCESS_TOKEN_EXP"))
    REFRESH_TOKEN_TTL: timedelta = timedelta(seconds=env.int("REFRESH_TOKEN_EXP"))
    CLIENT_EMAIL_KEY: ClassVar[str] = "client_email"
    CLIENT_ROLE_KEY: ClassVar[str] = "client_role"

    def _encode_jwt(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload=payload, key=self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)

    def _decode_jwt_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            jwt=token,
            key=self.JWT_SECRET_KEY,
            algorithms=self.ALGORITHM,
            options={"require": ["type", "exp", "iat", "nbf"]},
        )

    def validate_token(self, token: str) -> dict[str, Any]:
        return self._decode_jwt_token(token=token)

    def _sign_jwt_token(
            self,
            token_type: TokenType,
            subject: str,
            payload: dict[str, Any],
            ttl: timedelta = None,
    ) -> str:
        """Iss (issuer) — издатель токена; \n sub (subject) — субъект, которому
        выдан токен; \n aud (audience) — получатели, которым предназначается
        данный токен; \n iat (issued at) — время, в которое был выдан токен; \n
        nbf (not before) — время, с которого токен должен считаться
        действительным; \n jti (JWT ID) — уникальный идентификатор токена.

        \n exp (expiration time) — время, когда токен станет невалидным;
        \n

        """

        current_timestamp = convert_to_timestamp(datetime.now(tz=timezone.utc))
        data: dict[str, Any] = {
            self.ISSUER: "chmnu@auth_service",
            self.SUBJECT: subject,
            self.TOKEN_TYPE: token_type,
            self.ISSUED_AT: current_timestamp,
            self.NOT_BEFORE: payload[self.NOT_BEFORE] if payload.get(self.NOT_BEFORE) else current_timestamp,
        }
        data.update({self.EXPIRATION_TIME: data[self.NOT_BEFORE] + int(ttl.total_seconds())}) if ttl else None
        data.update(payload)

        return self._encode_jwt(payload=data)

    def _create_access_token(self, payload: dict[str, Any]) -> str:
        return self._sign_jwt_token(
            token_type=TokenType.ACCESS,
            subject=payload.get(self.CLIENT_EMAIL_KEY),
            payload=payload,
            ttl=self.ACCESS_TOKEN_TTL,
        )

    def _create_refresh_token(self, payload: dict[str, Any]) -> str:
        return self._sign_jwt_token(
            token_type=TokenType.REFRESH,
            subject=payload.get(self.CLIENT_EMAIL_KEY),
            payload=payload,
            ttl=self.REFRESH_TOKEN_TTL,
        )

    def create_tokens(self, client: ClientEntity) -> TokenEntity:
        payload: dict[str, Any] = {
            self.CLIENT_EMAIL_KEY: client.email,
            self.CLIENT_ROLE_KEY: client.role,
        }

        access_token = self._create_access_token(payload=payload)
        refresh_token = self._create_refresh_token(payload=payload)

        return TokenEntity(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def get_client_email_from_token(self, token: str) -> str:
        payload: dict[str, Any] = self._decode_jwt_token(token=token)
        user_email: str = payload.get(self.CLIENT_EMAIL_KEY)
        if not user_email:
            raise JWTKeyParsingException
        return user_email

    def get_client_role_from_token(self, token: str) -> str:
        payload: dict[str, Any] = self._decode_jwt_token(token=token)
        user_role: str = payload.get(self.CLIENT_ROLE_KEY)
        if not user_role:
            raise JWTKeyParsingException
        return user_role

    def get_token_type_from_token(self, token: str) -> TokenType:
        payload: dict[str, Any] = self._decode_jwt_token(token=token)
        token_type: str = payload.get(self.TOKEN_TYPE)
        if not token_type:
            raise JWTKeyParsingException
        return TokenType(token_type)
