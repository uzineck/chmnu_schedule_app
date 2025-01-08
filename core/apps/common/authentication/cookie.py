from ninja.security import APIKeyCookie

from core.apps.common.authentication.auth_check import AuthCheck


class JWTCookieAuth(AuthCheck, APIKeyCookie):
    openapi_in: str = "cookie"
    param_name: str = "access_token"
