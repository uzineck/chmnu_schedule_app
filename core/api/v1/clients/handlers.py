from django.http import (
    HttpRequest,
    HttpResponse,
)
from ninja import Router
from ninja.errors import HttpError

from jwt import PyJWTError

from core.api.schemas import (
    ApiErrorResponse,
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
    response={
        200: ApiResponse[ClientSchemaPrivate],
        401: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='get_client_info',
    auth=jwt_auth,
    summary="Get current client profile",
    description=(
        "Returns the authenticated client's profile (name, email, roles).\n\n"
        "Identity is resolved from the access token; no body or query parameters are accepted."
    ),
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
    response={
        200: ApiResponse[TokenOutSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='login',
    summary="Log in with email and password",
    description=(
        "Authenticates a client and issues a JWT pair. The access token is returned in the JSON body; "
        "the refresh token is set as an HttpOnly, SameSite=Strict cookie named `refresh_token` and is "
        "never exposed in the response body."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        401: ApiErrorResponse,
    },
    operation_id='logout',
    auth=jwt_auth,
    summary="Log out the current device",
    description=(
        "Revokes the access token for the calling device and clears the `refresh_token` cookie. "
        "Other devices remain logged in."
    ),
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
    response={
        200: ApiResponse[TokenOutSchema],
        401: ApiErrorResponse,
    },
    operation_id='update_access_token',
    summary="Refresh the access token",
    description=(
        "Issues a new access token using the `refresh_token` cookie. The refresh token itself is "
        "long-lived and is not rotated. Returns 401 if the cookie is missing, expired, or invalid."
    ),
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
    response={
        200: ApiResponse[StatusResponse],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
    },
    operation_id='update_password',
    auth=jwt_auth,
    summary="Change the current client's password",
    description=(
        "Updates the authenticated client's password. Requires the current password as `old_password`; "
        "`new_password` must equal `verify_password` and satisfy the password policy."
    ),
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
    response={
        200: ApiResponse[TokenClientOutSchema],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id='update_email',
    auth=jwt_auth,
    summary="Change the current client's email",
    description=(
        "Updates the authenticated client's email after re-verifying the password. Because the email "
        "is part of the JWT subject, a new access token is issued and a fresh `refresh_token` cookie "
        "is set."
    ),
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
    response={
        200: ApiResponse[ClientSchemaPrivate],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
    },
    operation_id='update_credentials',
    auth=jwt_auth,
    summary="Change the current client's name fields",
    description="Updates the authenticated client's first/last/middle name. Email and roles are not affected.",
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
    summary="Clear the refresh_token cookie",
    description=(
        "Removes the `refresh_token` cookie from the browser. Use this when the client side wants to "
        "wipe the cookie without going through the full `log-out` flow (e.g. after a 401 from "
        "`update_access_token`)."
    ),
)
def delete_cookies(request: HttpRequest, response: HttpResponse) -> ApiResponse[StatusResponse]:
    response.delete_cookie(key="refresh_token")
    return ApiResponse(
        data=StatusResponse(status="Successfully deleted cookie"),
    )
