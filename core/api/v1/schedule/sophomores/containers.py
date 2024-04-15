from core.apps.common.authentication import AuthenticationService
from core.apps.clients.services.sophomore import ORMSophomoreService
from core.apps.clients.services.auth import AuthService

authentication_service = AuthenticationService()

sophomore_service = ORMSophomoreService(auth_service=authentication_service)

sophomore_auth = AuthService(client_service=sophomore_service, authentication_service=authentication_service)
