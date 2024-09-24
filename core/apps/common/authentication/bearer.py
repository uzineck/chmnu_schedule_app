from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.security import HttpBearer

from jwt import PyJWTError

from core.apps.common.authentication.token import JWTTokenService
from core.apps.common.models import (
    ClientRole,
    TokenType,
)


class JWTBearer(HttpBearer):
    def __init__(self, allowed_roles: list[ClientRole] | None = None, allowed_emails: list[str] | None = None):
        super().__init__()
        self.allowed_roles = allowed_roles
        self.allowed_emails = allowed_emails

    def authenticate(self, request: HttpRequest, token: str) -> str:
        try:
            token_service = JWTTokenService()

            token_type = token_service.get_token_type_from_token(token=token)
            if token_type != TokenType.ACCESS:
                raise HttpError(
                    status_code=403,
                    message="Invalid token type",
                )

            user_role = token_service.get_client_role_from_token(token=token)
            if not self._is_role_allowed(role=user_role):
                raise HttpError(
                    status_code=403,
                    message="Client does not have permission to access this resource",
                )

            user_email = token_service.get_client_email_from_token(token=token)
            if not self._is_email_allowed(email=user_email):
                raise HttpError(
                    status_code=403,
                    message="Client does not have permission to access this resource",
                )

        except PyJWTError:
            raise HttpError(
                status_code=401,
                message="Invalid token",
            )
        return token

    def _is_role_allowed(self, role: str) -> bool:
        return role in self.allowed_roles

    def _is_email_allowed(self, email: str) -> bool:
        if not self.allowed_emails:
            return True
        return email in self.allowed_emails


jwt_bearer_admin = JWTBearer([ClientRole.ADMIN])
jwt_bearer_headman = JWTBearer([ClientRole.HEADMAN])
jwt_bearer_manager = JWTBearer([ClientRole.MANAGER])
jwt_bearer = JWTBearer([ClientRole.ADMIN, ClientRole.HEADMAN, ClientRole.MANAGER])
