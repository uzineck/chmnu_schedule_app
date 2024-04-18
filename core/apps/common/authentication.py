from abc import ABC, abstractmethod
from datetime import datetime
import bcrypt
import jwt

from typing import Any, ClassVar

from django.http import HttpRequest
from jwt import PyJWTError
from ninja.errors import HttpError
from ninja.security import HttpBearer

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity
from core.apps.clients.exceptions.sophomores import SophomoreEmailNotFoundException
from core.apps.clients.models import Sophomore as SophomoreModel
from core.apps.common.exceptions import ServiceException
from core.project.settings.main import env


class JWT(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> str:
        try:
            user_email = AuthenticationService().get_user_email_from_token(token=token)
            try:
                SophomoreModel.objects.get(email=user_email)
            except SophomoreModel.DoesNotExist:
                raise SophomoreEmailNotFoundException(email=user_email)
        except ServiceException as e:
            raise HttpError(
                status_code=401,
                message=e.message
            )
        except PyJWTError:
            raise HttpError(
                status_code=401,
                message="Invalid token"
            )
        return token


auth_bearer = JWT()


class BaseAuthenticationService(ABC):
    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        ...

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        ...

    @abstractmethod
    def create_jwt(self, sophomore: SophomoreEntity):
        ...

    @abstractmethod
    def get_user_email_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> str:
        ...


class AuthenticationService(BaseAuthenticationService):
    JWT_SECRET_KEY: ClassVar[str] = env("JWT_SECRET_KEY")
    ALGORITHM: ClassVar[str] = "HS256"
    USER_ID_KEY: ClassVar[str] = "user_id"
    USER_EMAIL_KEY: ClassVar[str] = "user_email"
    HASH_ENCODING: ClassVar[str] = "UTF-8"
    ACCESS_TOKEN_EXPIRATION_DELTA: ClassVar[int] = 600  # 10 minutes expiration
    REFRESH_TOKEN_EXPIRATION_DELTA: ClassVar[int] = 864000  # 10 days expiration

    # hash
    def hash_password(self, plain_password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password=plain_password.encode(self.HASH_ENCODING),
            salt=bcrypt.gensalt()
        )
        return hashed_password.decode(self.HASH_ENCODING)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password=plain_password.encode(self.HASH_ENCODING),
            hashed_password=hashed_password.encode(self.HASH_ENCODING)
        )

    # JWT
    def create_jwt(self, sophomore: SophomoreEntity) -> str:
        payload: dict[str, Any] = {
            self.USER_ID_KEY: sophomore.id,
            self.USER_EMAIL_KEY: sophomore.email,
        }

        return self._encode_jwt(payload=payload)

    def _encode_jwt(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload=payload, key=self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)

    def get_user_email_from_token(self, token: str) -> str:
        payload: dict[str, Any] = self._decode_jwt_token(token=token)
        user_email: str = payload.get(self.USER_EMAIL_KEY)
        if not user_email:
            raise JWTKeyParsingException
        return user_email

    def get_user_id_from_token(self, token: str) -> int:
        payload: dict[str, Any] = self._decode_jwt_token(token=token)
        user_id: int = payload.get(self.USER_ID_KEY)
        if not user_id:
            raise JWTKeyParsingException
        return user_id

    def _decode_jwt_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(jwt=token, key=self.JWT_SECRET_KEY, algorithms=self.ALGORITHM)
