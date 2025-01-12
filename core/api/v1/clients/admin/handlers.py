from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import (
    ApiResponse,
    StatusResponse,
)
from core.api.v1.clients.schemas import (
    ClientSchemaPrivate,
    RolesInSchema,
    SignUpInSchema,
    UpdatePwInAdminSchema,
)
from core.apps.clients.usecases.admin.update_password import UpdateClientPasswordAdminUseCase
from core.apps.clients.usecases.admin.update_role import UpdateClientRoleUseCase
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.get_info import GetClientInfoUseCase
from core.apps.common.authentication.ninja_auth import jwt_auth_client_manager
from core.apps.common.cache.service import BaseCacheService
from core.apps.common.cache.timeouts import Timeout
from core.apps.common.exceptions import ServiceException
from core.project.containers.containers import get_container


router = Router(tags=["Admin"])


@router.get(
    "{client_email}/info",
    response={200: ApiResponse[ClientSchemaPrivate]},
    operation_id='get_client_info_admin',
    auth=jwt_auth_client_manager,
)
def get_client_info(request: HttpRequest, client_email: str) -> ApiResponse[ClientSchemaPrivate]:
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


@router.post(
    "sign-up",
    response={201: ApiResponse[ClientSchemaPrivate]},
    operation_id='sign_up',
    auth=jwt_auth_client_manager,
)
def sign_up(request: HttpRequest, schema: SignUpInSchema) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    use_case: CreateClientUseCase = container.resolve(CreateClientUseCase)
    try:
        client = use_case.execute(
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
            roles=schema.roles,
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
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.patch(
    "{client_email}/update_password",
    response=ApiResponse[StatusResponse],
    operation_id='update_password_admin',
    auth=jwt_auth_client_manager,
)
def update_password(
        request: HttpRequest,
        client_email: str,
        schema: UpdatePwInAdminSchema,
) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: UpdateClientPasswordAdminUseCase = container.resolve(UpdateClientPasswordAdminUseCase)

    try:
        use_case.execute(
            email=client_email,
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
    "{client_email}/update_roles",
    response=ApiResponse[ClientSchemaPrivate],
    operation_id='update_client_roles',
    auth=jwt_auth_client_manager,
)
def update_client_roles(
        request: HttpRequest,
        client_email: str,
        schema: RolesInSchema,
) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    cache_service: BaseCacheService = container.resolve(BaseCacheService)
    use_case: UpdateClientRoleUseCase = container.resolve(UpdateClientRoleUseCase)
    try:
        client = use_case.execute(
            email=client_email,
            roles=schema.roles,
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
