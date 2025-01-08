from core.apps.common.authentication.bearer import JWTBearer
from core.apps.common.models import ClientRole


jwt_auth_admin = JWTBearer([ClientRole.ADMIN])
jwt_auth_headman = JWTBearer([ClientRole.HEADMAN])
jwt_auth_manager = JWTBearer([ClientRole.MANAGER])
jwt_auth = JWTBearer([ClientRole.ADMIN, ClientRole.HEADMAN, ClientRole.MANAGER])
