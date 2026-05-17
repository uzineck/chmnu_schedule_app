from django.http import (
    HttpRequest,
    HttpResponse,
)
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
    TokenClientOutSchema,
    TokenOutSchema,
    UpdateEmailInSchema,
    UpdatePwInSchema,
)
from core.apps.clients.usecases.client.get_info import GetClientInfoUseCase
from core.apps.clients.usecases.client.login import LoginClientUseCase
from core.apps.clients.usecases.client.logout import LogoutClientUseCase
from core.apps.clients.usecases.client.update_access_token import UpdateAccessTokenUseCase
from core.apps.clients.usecases.client.update_credentials import UpdateClientCredentialsUseCase
from core.apps.clients.usecases.client.update_email import UpdateClientEmailUseCase
from core.apps.clients.usecases.client.update_password import UpdateClientPasswordUseCase
from core.apps.common.authentication.ninja_auth import jwt_auth
from core.project.containers.containers import get_container


router = Router(tags=["Client"])


@router.get(
    "info",
    response={200: ApiResponse[ClientSchemaPrivate]},
    operation_id='get_client_info',
    auth=jwt_auth,
)
def get_client_info(request: HttpRequest) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    use_case: GetClientInfoUseCase = container.resolve(GetClientInfoUseCase)
    client = use_case.execute(email=request.client_email)

    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.post(
    "log-in",
    response=ApiResponse[TokenOutSchema],
    operation_id='login',
)
def login(request: HttpRequest, response: HttpResponse, schema: LogInSchema) -> ApiResponse[TokenOutSchema]:
    container = get_container()
    use_case: LoginClientUseCase = container.resolve(LoginClientUseCase)
    client, jwt_tokens = use_case.execute(email=schema.email, password=schema.password)
    response.set_cookie(key="refresh_token", value=jwt_tokens.refresh_token, httponly=True, samesite="Strict")

    return ApiResponse(
        data=TokenOutSchema.from_values(access_token=jwt_tokens.access_token),
    )


@router.post(
    "log-out",
    response=ApiResponse[StatusResponse],
    operation_id='logout',
    auth=jwt_auth,
)
def logout(request: HttpRequest, response: HttpResponse) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: LogoutClientUseCase = container.resolve(LogoutClientUseCase)
    use_case.execute(client_email=request.client_email, device_id=request.device_id)
    response.delete_cookie(key="refresh_token")

    return ApiResponse(
        data=StatusResponse(status="Successfully logged out"),
    )


@router.post(
    "update_access_token",
    response=ApiResponse[TokenOutSchema],
    operation_id='update_access_token',
)
def update_access_token(request: HttpRequest) -> ApiResponse[TokenOutSchema]:
    container = get_container()
    use_case: UpdateAccessTokenUseCase = container.resolve(UpdateAccessTokenUseCase)

    try:
        jwt_tokens = use_case.execute(refresh_token=request.COOKIES.get("refresh_token"))
    except PyJWTError:
        raise HttpError(
            status_code=401,
            message='Invalid token uat',
        )
    return ApiResponse(
        data=TokenOutSchema.from_values(access_token=jwt_tokens.access_token),
    )


@router.patch(
    "update_password",
    response=ApiResponse[StatusResponse],
    operation_id='update_password',
    auth=jwt_auth,
)
def update_password(request: HttpRequest, schema: UpdatePwInSchema) -> ApiResponse[StatusResponse]:
    container = get_container()
    use_case: UpdateClientPasswordUseCase = container.resolve(UpdateClientPasswordUseCase)

    use_case.execute(
        email=request.client_email,
        old_password=schema.old_password,
        new_password=schema.new_password,
        verify_password=schema.verify_password,
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
    auth=jwt_auth,
)
def update_email(
        request: HttpRequest,
        response: HttpResponse,
        schema: UpdateEmailInSchema,
) -> ApiResponse[TokenClientOutSchema]:
    container = get_container()
    use_case: UpdateClientEmailUseCase = container.resolve(UpdateClientEmailUseCase)

    client, jwt_tokens = use_case.execute(
        old_email=request.client_email,
        new_email=schema.new_email,
        password=schema.password,
    )
    response.set_cookie(key="refresh_token", value=jwt_tokens.refresh_token, httponly=True, samesite="Strict")

    return ApiResponse(
        data=TokenClientOutSchema.from_entity_with_token_values(client=client, access_token=jwt_tokens.access_token),
    )


@router.patch(
    "update_credentials",
    response=ApiResponse[ClientSchemaPrivate],
    operation_id='update_credentials',
    auth=jwt_auth,
)
def update_credentials(request: HttpRequest, schema: CredentialsInSchema) -> ApiResponse[ClientSchemaPrivate]:
    container = get_container()
    use_case: UpdateClientCredentialsUseCase = container.resolve(UpdateClientCredentialsUseCase)

    client = use_case.execute(
        email=request.client_email,
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
    )
    return ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.post(
    "delete_cookie",
    response=ApiResponse[StatusResponse],
    operation_id='delete_cookie',
)
def delete_cookies(request: HttpRequest, response: HttpResponse) -> ApiResponse[StatusResponse]:
    response.delete_cookie(key="refresh_token")
    return ApiResponse(
        data=StatusResponse(status="Successfully deleted cookie"),
    )
