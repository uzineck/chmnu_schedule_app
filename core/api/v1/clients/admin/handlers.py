from django.http import HttpRequest
from ninja import Router

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
    use_case: GetClientInfoUseCase = container.resolve(GetClientInfoUseCase)
    client = use_case.execute(email=client_email)

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
    client = use_case.execute(
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
        roles=schema.roles,
        email=schema.email,
        password=schema.password,
        verify_password=schema.verify_password,
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

    use_case.execute(
        email=client_email,
        new_password=schema.new_password,
        verify_password=schema.verify_password,
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
    use_case: UpdateClientRoleUseCase = container.resolve(UpdateClientRoleUseCase)
    client = use_case.execute(
        email=client_email,
        roles=schema.roles,
    )
    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )
