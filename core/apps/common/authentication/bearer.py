from ninja.security import HttpBearer

from core.apps.common.authentication.auth_check import AuthCheck


class JWTBearer(AuthCheck, HttpBearer):
    pass
