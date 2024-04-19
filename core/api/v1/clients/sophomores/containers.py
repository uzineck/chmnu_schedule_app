from core.apps.clients.services.update import UpdateUserService
from core.apps.clients.services.sophomore import ORMSophomoreService
from core.apps.clients.services.auth import AuthService
from core.apps.common.authentication.password import BcryptPasswordService
from core.apps.common.authentication.token import JWTTokenService

password_service = BcryptPasswordService()
token_service = JWTTokenService()

sophomore_service = ORMSophomoreService(password_service=password_service, token_service=token_service)

sophomore_auth = AuthService(client_service=sophomore_service)

sophomore_update = UpdateUserService(client_service=sophomore_service)
