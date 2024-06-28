import jwt
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    ClassVar,
)

from core.apps.clients.entities.client import Sophomore as SophomoreEntity
from core.apps.common.exceptions import JWTKeyParsingException
from core.project.settings.main import env


class BaseTokenService(ABC):
    @abstractmethod
    def create_token(self, sophomore: SophomoreEntity):
        ...

    @abstractmethod
    def get_user_email_from_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> int:
        ...

    # @abstractmethod
    # def get_sophomore_group_from_token(self, token: str) -> str:
    #     ...


class JWTTokenService(BaseTokenService):
    JWT_SECRET_KEY: ClassVar[str] = env("JWT_SECRET_KEY")
    ALGORITHM: ClassVar[str] = "HS256"
    USER_ID_KEY: ClassVar[str] = "user_id"
    USER_EMAIL_KEY: ClassVar[str] = "user_email"
    SOPHOMORE_GROUP_KEY: ClassVar[str] = 'sophomore_group'
    ACCESS_TOKEN_EXPIRATION_DELTA: ClassVar[int] = 600  # 10 minutes expiration
    REFRESH_TOKEN_EXPIRATION_DELTA: ClassVar[int] = 864000  # 10 days expiration

    def _encode_jwt(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload=payload, key=self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)

    def _decode_jwt_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(jwt=token, key=self.JWT_SECRET_KEY, algorithms=self.ALGORITHM)

    def create_token(self, sophomore: SophomoreEntity):
        payload: dict[str, Any] = {
            self.USER_ID_KEY: sophomore.id,
            self.USER_EMAIL_KEY: sophomore.email,
        }

        return self._encode_jwt(payload=payload)

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
