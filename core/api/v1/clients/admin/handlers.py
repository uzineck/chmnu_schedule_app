from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError
from ninja.security import django_auth_superuser

from core.api.schemas import ApiResponse
from core.api.v1.clients.schemas import (
    ClientSchema,
    SignUpInSchema,
    UpdateGroupHeadmanSchema,
    UpdateRoleInSchema,
)
from core.api.v1.schedule.groups.schemas import GroupSchema
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.update_role import UpdateClientRoleUseCase
from core.apps.common.exceptions import ServiceException
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase
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
    container.resolve(BaseClientService)
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


@router.patch(
    "update_group_headman",
    response=ApiResponse[GroupSchema],
    operation_id='update_group_headman',
    auth=django_auth_superuser,
)
def update_group_headman(request: HttpRequest, schema: UpdateGroupHeadmanSchema) -> ApiResponse[GroupSchema]:
    container = get_container()
    use_case: UpdateGroupHeadmanUseCase = container.resolve(UpdateGroupHeadmanUseCase)
    try:
        group = use_case.execute(
            group_number=schema.group_number,
            headman_email=schema.headman_email,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=GroupSchema(
            number=group.number,
            headman=group.headman,
            has_subgroups=group.has_subgroups,
        ),
    )
