from core.apps.common.authentication.cookie import JWTCookieAuth
from core.apps.common.models import ClientRole


jwt_auth_admin = JWTCookieAuth([ClientRole.ADMIN])
jwt_auth_headman = JWTCookieAuth([ClientRole.HEADMAN])
jwt_auth_manager = JWTCookieAuth([ClientRole.MANAGER])
jwt_auth = JWTCookieAuth([ClientRole.ADMIN, ClientRole.HEADMAN, ClientRole.MANAGER])
