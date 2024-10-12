from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.clients.schemas import (
    ClientSchemaPrivate,
    SignUpInSchema,
    TokenClientOutSchema,
    UpdateRoleInSchema,
)
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.update_role import UpdateClientRoleUseCase
from core.apps.common.authentication.bearer import jwt_bearer_admin
from core.apps.common.exceptions import ServiceException
from core.project.containers.containers import get_container


router = Router(tags=["Admin"])


@router.post("sign-up", response=ApiResponse[ClientSchemaPrivate], operation_id='sign_up', auth=jwt_bearer_admin)
def sign_up_handler(request: HttpRequest, schema: SignUpInSchema) -> ApiResponse[ClientSchemaPrivate]:
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
            verify_password=schema.verify_password,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.patch(
    "update_client_role",
    response=ApiResponse[TokenClientOutSchema],
    operation_id='update_client_role',
    auth=jwt_bearer_admin,
)
def update_client_role(request: HttpRequest, schema: UpdateRoleInSchema) -> ApiResponse[TokenClientOutSchema]:
    container = get_container()
    use_case: UpdateClientRoleUseCase = container.resolve(UpdateClientRoleUseCase)
    try:
        client, jwt_tokens = use_case.execute(
            email=schema.client_email,
            new_role=schema.role,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=TokenClientOutSchema.from_entity_with_tokens(client=client, tokens=jwt_tokens),
    )
