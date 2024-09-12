from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import (
    ApiResponse,
    StatusResponse,
)
from core.api.v1.clients.schemas import (
    ClientSchema,
    LogInSchema,
    TokenOutSchema,
    UpdateCredentialsInSchema,
    UpdateEmailInSchema,
    UpdatePwInSchema,
)
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.usecases.client.login import LoginClientUseCase
from core.apps.clients.usecases.client.update_credentials import UpdateClientCredentialsUseCase
from core.apps.clients.usecases.client.update_email import UpdateClientEmailUseCase
from core.apps.clients.usecases.client.update_password import UpdateClientPasswordUseCase
from core.apps.common.authentication.bearer import jwt_bearer
from core.apps.common.exceptions import (
    JWTKeyParsingException,
    ServiceException,
)
from core.project.containers import get_container


router = Router(tags=["Client"])


@router.post("log-in", response=ApiResponse[TokenOutSchema], operation_id='login')
def login_handler(request: HttpRequest, schema: LogInSchema) -> ApiResponse[TokenOutSchema]:
    container = get_container()
    use_case = container.resolve(LoginClientUseCase)
    try:
        client, jwt_token = use_case.execute(email=schema.email, password=schema.password)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=TokenOutSchema.from_entity_with_token(client=client, token=jwt_token),
    )


@router.patch(
    "update_password",
    response=ApiResponse[StatusResponse],
    operation_id='update_password',
    auth=jwt_bearer,
)
def update_password(request: HttpRequest, schema: UpdatePwInSchema) -> ApiResponse[StatusResponse]:
    container = get_container()
    client_service = container.resolve(BaseClientService)
    use_case = container.resolve(UpdateClientPasswordUseCase)
    try:
        user_email: str = client_service.get_user_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    try:
        use_case.execute(
            email=user_email,
            old_password=schema.old_password,
            new_password=schema.new_password,
            verify_password=schema.verify_password,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message,
        )

    return ApiResponse(
        data=StatusResponse(
            status="Password updated successfully",
        ),
    )


@router.patch(
    "update_email",
    response=ApiResponse[TokenOutSchema],
    operation_id='update_email',
    auth=jwt_bearer,
)
def update_email(request: HttpRequest, schema: UpdateEmailInSchema) -> ApiResponse[TokenOutSchema]:
    container = get_container()
    client_service = container.resolve(BaseClientService)
    use_case = container.resolve(UpdateClientEmailUseCase)
    try:
        user_email: str = client_service.get_user_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    try:
        client, jwt_token = use_case.execute(
            old_email=user_email,
            new_email=schema.new_email,
            password=schema.password,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=TokenOutSchema.from_entity_with_token(client=client, token=jwt_token),
    )


@router.patch(
    "update_credentials",
    response=ApiResponse[ClientSchema],
    operation_id='update_credentials',
    auth=jwt_bearer,
)
def update_credentials(
    request: HttpRequest,
    schema: UpdateCredentialsInSchema,
) -> ApiResponse[ClientSchema]:
    container = get_container()
    client_service = container.resolve(BaseClientService)
    use_case = container.resolve(UpdateClientCredentialsUseCase)
    try:
        user_email: str = client_service.get_user_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message,
        )

    try:
        client = use_case.execute(
            email=user_email,
            first_name=schema.first_name,
            last_name=schema.last_name,
            middle_name=schema.middle_name,
        )
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message,
        )
    return ApiResponse(
        data=ClientSchema.from_entity(client=client),
    )
