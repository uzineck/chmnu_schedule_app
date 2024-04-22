from django.http import HttpRequest
from jwt import PyJWTError
from ninja.errors import HttpError
from ninja.security import HttpBearer

from core.apps.clients.exceptions.sophomores import SophomoreEmailNotFoundException
from core.apps.clients.models import Sophomore as SophomoreModel
from core.apps.common.authentication.token import JWTTokenService
from core.apps.common.exceptions import ServiceException


class JWTBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> str:
        try:
            JWTTokenService().get_user_email_from_token(token=token)
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


jwt_bearer = JWTBearer()
