import punq

from core.apps.clients.services.client import (
    BaseClientService,
    ORMClientService,
)
from core.apps.clients.services.issuedjwttoken import (
    BaseIssuedJwtTokenService,
    ORMIssuedJwtTokenService,
)
from core.apps.clients.services.role import (
    BaseRoleService,
    ORMRoleService,
)
from core.apps.clients.usecases.admin.update_password import UpdateClientPasswordAdminUseCase
from core.apps.clients.usecases.admin.update_role import UpdateClientRoleUseCase
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.get_info import GetClientInfoUseCase
from core.apps.clients.usecases.client.login import LoginClientUseCase
from core.apps.clients.usecases.client.logout import LogoutClientUseCase
from core.apps.clients.usecases.client.update_access_token import UpdateAccessTokenUseCase
from core.apps.clients.usecases.client.update_credentials import UpdateClientCredentialsUseCase
from core.apps.clients.usecases.client.update_email import UpdateClientEmailUseCase
from core.apps.clients.usecases.client.update_password import UpdateClientPasswordUseCase
from core.apps.clients.usecases.headman.get_headman_group import GetHeadmanGroupUseCase
from core.apps.common.authentication.password import (
    BasePasswordService,
    BcryptPasswordService,
)
from core.apps.common.authentication.token import (
    BaseTokenService,
    JWTTokenService,
)


def register_client_services(container: punq.Container):
    container.register(BaseClientService, ORMClientService)
    container.register(BasePasswordService, BcryptPasswordService)
    container.register(BaseTokenService, JWTTokenService)
    container.register(BaseIssuedJwtTokenService, ORMIssuedJwtTokenService)
    container.register(BaseRoleService, ORMRoleService)

    container.register(CreateClientUseCase)
    container.register(LoginClientUseCase)
    container.register(LogoutClientUseCase)
    container.register(UpdateClientEmailUseCase)
    container.register(UpdateClientPasswordUseCase)
    container.register(UpdateClientCredentialsUseCase)
    container.register(UpdateClientRoleUseCase)
    container.register(GetHeadmanGroupUseCase)
    container.register(GetClientInfoUseCase)
    container.register(UpdateAccessTokenUseCase)

    container.register(UpdateClientPasswordAdminUseCase)
