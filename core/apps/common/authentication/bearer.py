from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.security import HttpBearer

from jwt import PyJWTError

from core.apps.common.authentication.token import JWTTokenService
from core.apps.common.exceptions import ServiceException
from core.apps.common.models import ClientRole


class JWTBearer(HttpBearer):
    def __init__(self, allowed_roles=None):
        super().__init__()
        self.allowed_roles = allowed_roles or [ClientRole.DEFAULT]

    def authenticate(self, request: HttpRequest, token: str) -> str:
        try:
            token_service = JWTTokenService()
            user_role = token_service.get_user_role_from_token(token=token)

            if not self.is_role_allowed(user_role):
                raise HttpError(
                    status_code=403,
                    message="Client does not have permission to access this resource",
                )

        except ServiceException as e:
            raise HttpError(
                status_code=401,
                message=e.message,
            )
        except PyJWTError:
            raise HttpError(
                status_code=401,
                message="Invalid token",
            )
        return token

    def is_role_allowed(self, role: str) -> bool:
        return role in self.allowed_roles


jwt_bearer_admin = JWTBearer([ClientRole.ADMIN])
jwt_bearer_headman = JWTBearer([ClientRole.HEADMAN])
jwt_bearer = JWTBearer([ClientRole.ADMIN, ClientRole.HEADMAN])

