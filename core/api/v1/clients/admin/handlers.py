from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError
from ninja.security import django_auth_superuser

from core.api.schemas import ApiResponse
from core.api.v1.clients.schemas import (
    ClientEmailInSchema,
    ClientSchema,
    SignUpInSchema,
    UpdateRoleInSchema,
)
from core.api.v1.schedule.groups.schemas import GroupSchema
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.update_role import UpdateClientRoleUseCase
from core.apps.clients.usecases.headman.get_headman_info import GetHeadmanInfoUseCase
from core.apps.common.exceptions import ServiceException
from core.project.containers import get_container


router = Router(tags=["Admin"])


@router.post("sign-up", response=ApiResponse[ClientSchema], operation_id='sign_up', auth=django_auth_superuser)
def sign_up_handler(request: HttpRequest, schema: SignUpInSchema) -> ApiResponse[ClientSchema]:
    container = get_container()
    use_case = container.resolve(CreateClientUseCase)
    try:
        client = use_case.execute(
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
            role=schema.role,
            email=schema.email,
            password=schema.password,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=ClientSchema(
            last_name=client.last_name,
            first_name=client.first_name,
            middle_name=client.middle_name,
            role=client.role,
            email=client.email,
        ),
    )


@router.patch(
    "update_client_role",
    response=ApiResponse[ClientSchema],
    operation_id='update_client_role',
    auth=django_auth_superuser,
)
def update_client_role(request: HttpRequest, schema: UpdateRoleInSchema) -> ApiResponse[ClientSchema]:
    container = get_container()
    use_case = container.resolve(UpdateClientRoleUseCase)
    try:
        client, jwt_token = use_case.execute(
            client_email=schema.email,
            new_role=schema.role,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=ClientSchema(
            last_name=client.last_name,
            first_name=client.first_name,
            middle_name=client.middle_name,
            role=client.role,
            email=client.email,
        ),
    )


@router.post(
    "get_headman_info",
    response=ApiResponse[GroupSchema],
    operation_id='get_headman_info',
    auth=django_auth_superuser,
)
def get_headman_info(request: HttpRequest, schema: ClientEmailInSchema) -> ApiResponse[GroupSchema]:
    container = get_container()
    use_case: GetHeadmanInfoUseCase = container.resolve(GetHeadmanInfoUseCase)
    try:
        group, headman = use_case.execute(
            email=schema.email,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=GroupSchema(
            number=group.number,
            headman=headman,
            has_subgroups=group.has_subgroups,
        ),
    )
