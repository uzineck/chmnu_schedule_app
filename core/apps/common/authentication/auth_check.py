from django.http import HttpRequest
from ninja.errors import HttpError

from jwt import PyJWTError

from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.authentication.token import (
    BaseTokenService,
    JWTTokenService,
)
from core.apps.common.exceptions import JWTKeyParsingException
from core.apps.common.models import (
    ClientRole,
    TokenType,
)
from core.project.containers.containers import get_container


class AuthCheck:
    def __init__(self, allowed_roles: list[ClientRole], allowed_emails: list[str] | None = None):
        super().__init__()
        self.allowed_roles = allowed_roles
        self.allowed_emails = allowed_emails

    def authenticate(self, request: HttpRequest, token: str) -> str:
        container = get_container()
        token_service: BaseTokenService = container.resolve(BaseTokenService)
        issued_jwt_token_service: BaseIssuedJwtTokenService = container.resolve(BaseIssuedJwtTokenService)

        try:
            payload = token_service.decode_token(token=token)
        except PyJWTError:
            raise HttpError(
                status_code=401,
                message="Invalid token",
            )

        token_type = self._require(payload, JWTTokenService.TOKEN_TYPE)
        if TokenType(token_type) != TokenType.ACCESS:
            raise HttpError(
                status_code=401,
                message="Invalid token type",
            )

        jti = self._require(payload, JWTTokenService.JWT_ID)
        if issued_jwt_token_service.check_revoked(jti=jti):
            raise HttpError(
                status_code=401,
                message="Revoked token",
            )

        raw_roles = self._require(payload, JWTTokenService.CLIENT_ROLE_KEY)
        client_roles = [ClientRole(role) for role in raw_roles]
        if not self._is_role_allowed(roles=client_roles):
            raise HttpError(
                status_code=403,
                message="Client does not have permission to access this resource",
            )

        client_email = self._require(payload, JWTTokenService.CLIENT_EMAIL_KEY)
        if not self._is_email_allowed(email=client_email):
            raise HttpError(
                status_code=403,
                message="Client does not have permission to access this resource",
            )

        request.client_email = client_email
        request.client_roles = client_roles
        request.token_jti = jti
        request.device_id = payload.get(JWTTokenService.DEVICE_ID)
        request.token_expiration = payload.get(JWTTokenService.EXPIRATION_TIME)

        return token

    @staticmethod
    def _require(payload: dict, key: str):
        value = payload.get(key)
        if value is None:
            raise JWTKeyParsingException
        return value

    def _is_role_allowed(self, roles: list[ClientRole]) -> bool:
        return any(role in self.allowed_roles for role in roles)

    def _is_email_allowed(self, email: str) -> bool:
        if not self.allowed_emails:
            return True
        return email in self.allowed_emails
