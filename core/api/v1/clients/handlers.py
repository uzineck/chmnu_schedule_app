from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from jwt import PyJWTError

from core.api.schemas import (
    ApiResponse,
    StatusResponse,
)
from core.api.v1.clients.schemas import (
    ClientSchemaPrivate,
    CredentialsInSchema,
    LogInSchema,
    RoleInSchema,
    SignUpInSchema,
    TokenClientOutSchema,
    TokenInSchema,
    TokenOutSchema,
    UpdateEmailInSchema,
    UpdatePwInSchema,
)
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.usecases.admin.update_role import UpdateClientRoleUseCase
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.get_info import GetClientInfoUseCase
from core.apps.clients.usecases.client.login import LoginClientUseCase
from core.apps.clients.usecases.client.logout import LogoutClientUseCase
from core.apps.clients.usecases.client.update_access_token import UpdateAccessTokenUseCase
from core.apps.clients.usecases.client.update_credentials import UpdateClientCredentialsUseCase
from core.apps.clients.usecases.client.update_email import UpdateClientEmailUseCase
from core.apps.clients.usecases.client.update_password import UpdateClientPasswordUseCase
from core.apps.common.authentication.bearer import (
    jwt_bearer,
    jwt_bearer_admin,
)
from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.exceptions import ServiceException
from core.project.containers.containers import get_container


router = Router(tags=["Client"])


@router.get(
    "{client_email}/info",
    response={200: ApiResponse[ClientSchemaPrivate]},
    operation_id='get_client_info_admin',
    auth=jwt_bearer_admin,
)
def get_client_info_admin(request: HttpRequest, client_email: str) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: GetClientInfoUseCase = container.resolve(GetClientInfoUseCase)
    try:
        cache_key = cache_service.generate_cache_key(
            model_prefix="client",
            identifier=client_email,
            func_prefix="info",
        )
        client = cache_service.get_cache_value(key=cache_key)
        if not client:
            client = use_case.execute(client_email)
            cache_service.set_cache(key=cache_key, value=client, timeout=Timeout.MONTH)

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.get(
    "info",
    response={200: ApiResponse[ClientSchemaPrivate]},
    operation_id='get_client_info',
    auth=jwt_bearer,
)
def get_client_info(request: HttpRequest) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    client_service: BaseClientService = container.resolve(BaseClientService)
    use_case: GetClientInfoUseCase = container.resolve(GetClientInfoUseCase)
    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
        cache_key = cache_service.generate_cache_key(
            model_prefix="client",
            identifier=user_email,
            func_prefix="info",
        )
        client = cache_service.get_cache_value(key=cache_key)
        if not client:
            client = use_case.execute(user_email)
            cache_service.set_cache(key=cache_key, value=client, timeout=Timeout.MONTH)

    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.post(
    "sign-up",
    response={201: ApiResponse[StatusResponse]},
    operation_id='sign_up',
    auth=jwt_bearer_admin,
)
def sign_up(request: HttpRequest, schema: SignUpInSchema) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: CreateClientUseCase = container.resolve(CreateClientUseCase)
    try:
        use_case.execute(
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
            role=schema.role,
            email=schema.email,
            password=schema.password,
            verify_password=schema.verify_password,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(status="Client successfully created"),
    )


@router.post(
    "log-in",
    response=ApiResponse[TokenClientOutSchema],
    operation_id='login',
)
def login(request: HttpRequest, schema: LogInSchema) -> ApiResponse[TokenClientOutSchema]:
    container = get_container()
    use_case: LoginClientUseCase = container.resolve(LoginClientUseCase)
    try:
        client, jwt_tokens = use_case.execute(email=schema.email, password=schema.password)
    except ServiceException:
        raise HttpError(
            status_code=400,
            message='Invalid email or password',
        )
    return ApiResponse(
        data=TokenClientOutSchema.from_entity_with_tokens(client=client, tokens=jwt_tokens),
    )


@router.post(
    "log-out",
    response=ApiResponse[StatusResponse],
    operation_id='logout',
    auth=jwt_bearer,
)
def logout(request: HttpRequest) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: LogoutClientUseCase = container.resolve(LogoutClientUseCase)
    try:
        use_case.execute(token=request.auth)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=StatusResponse(status="Successfully logged out"),
    )


@router.post(
    "update_access_token",
    response=ApiResponse[TokenOutSchema],
    operation_id='update_access_token',
)
def update_access_token(request: HttpRequest, schema: TokenInSchema) -> ApiResponse[TokenOutSchema]:
    container = get_container()
    use_case: UpdateAccessTokenUseCase = container.resolve(UpdateAccessTokenUseCase)

    try:
        access_token = use_case.execute(token=schema.token)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    except PyJWTError:
        raise HttpError(
            status_code=401,
            message='Invalid token',
        )
    return ApiResponse(
        data=TokenOutSchema.from_entity(tokens_entity=access_token),
    )


@router.patch(
    "update_password",
    response=ApiResponse[StatusResponse],
    operation_id='update_password',
    auth=jwt_bearer,
)
def update_password(request: HttpRequest, schema: UpdatePwInSchema) -> ApiResponse[StatusResponse]:
    container = get_container()
    client_service: BaseClientService = container.resolve(BaseClientService)
    use_case: UpdateClientPasswordUseCase = container.resolve(UpdateClientPasswordUseCase)

    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
        use_case.execute(
            email=user_email,
            old_password=schema.old_password,
            new_password=schema.new_password,
            verify_password=schema.verify_password,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(
            status="Password updated successfully",
        ),
    )


@router.patch(
    "update_email",
    response=ApiResponse[TokenClientOutSchema],
    operation_id='update_email',
    auth=jwt_bearer,
)
def update_email(request: HttpRequest, schema: UpdateEmailInSchema) -> ApiResponse[TokenClientOutSchema]:
    container = get_container()
    client_service = container.resolve(BaseClientService)
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateClientEmailUseCase = container.resolve(UpdateClientEmailUseCase)

    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
        client, jwt_tokens = use_case.execute(
            old_email=user_email,
            new_email=schema.new_email,
            password=schema.password,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier=user_email,
                    func_prefix="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="client",
                    identifier=user_email,
                    func_prefix="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=TokenClientOutSchema.from_entity_with_tokens(client=client, tokens=jwt_tokens),
    )


@router.patch(
    "update_credentials",
    response=ApiResponse[ClientSchemaPrivate],
    operation_id='update_credentials',
    auth=jwt_bearer,
)
def update_credentials(request: HttpRequest, schema: CredentialsInSchema) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    client_service: BaseClientService = container.resolve(BaseClientService)
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateClientCredentialsUseCase = container.resolve(UpdateClientCredentialsUseCase)

    try:
        user_email: str = client_service.get_client_email_from_token(token=request.auth)
        client = use_case.execute(
            email=user_email,
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier=user_email,
                    func_prefix="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="client",
                    identifier=user_email,
                    func_prefix="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.patch(
    "{client_email}/update_role",
    response=ApiResponse[ClientSchemaPrivate],
    operation_id='update_client_role',
    auth=jwt_bearer_admin,
)
def update_client_role(
        request: HttpRequest,
        client_email: str,
        schema: RoleInSchema,
) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateClientRoleUseCase = container.resolve(UpdateClientRoleUseCase)
    try:
        client = use_case.execute(
            email=client_email,
            new_role=schema.role,
        )
        cache_service.invalidate_cache_pattern_list(
            keys=[
                cache_service.generate_cache_key(
                    model_prefix="group",
                    identifier=client_email,
                    func_prefix="*",
                ),
                cache_service.generate_cache_key(
                    model_prefix="client",
                    identifier=client_email,
                    func_prefix="*",
                ),
            ],
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )
