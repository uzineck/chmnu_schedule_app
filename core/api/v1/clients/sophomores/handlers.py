from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import ApiResponse, StatusResponse
from core.api.v1.clients.sophomores.schemas import SignUpInSchema, LogInSchema, \
    UpdateEmailInSchema, UpdatePwInSchema, UpdateCredentialsInSchema, SophomoreSchema, TokenOutSchema
from core.api.v1.clients.sophomores.containers import sophomore_auth, sophomore_service, sophomore_update
from core.apps.common.authentication import auth_bearer
from core.apps.common.exceptions import ServiceException, JWTKeyParsingException

router = Router(tags=["Sophomores"])


@router.post("sign_up", response=ApiResponse[SophomoreSchema], operation_id='sign_up')
def sign_up_handler(request: HttpRequest, schema: SignUpInSchema) -> ApiResponse[SophomoreSchema]:
    try:
        sophomore = sophomore_auth.sign_up(first_name=schema.first_name,
                                           last_name=schema.last_name,
                                           middle_name=schema.middle_name,
                                           email=schema.email,
                                           password=schema.password)
    except ServiceException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    return ApiResponse(data=SophomoreSchema(
        last_name=sophomore.last_name,
        first_name=sophomore.first_name,
        middle_name=sophomore.middle_name,
        email=sophomore.email
    ))


@router.post("login", response=ApiResponse[TokenOutSchema], operation_id='login')
def login_handler(request: HttpRequest, schema: LogInSchema) -> ApiResponse[TokenOutSchema]:
    try:
        sophomore, jwt_token = sophomore_auth.login(email=schema.email, password=schema.password)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message
        )
    return ApiResponse(data=TokenOutSchema(
        last_name=sophomore.last_name,
        first_name=sophomore.first_name,
        middle_name=sophomore.middle_name,
        email=sophomore.email,
        token=jwt_token,
    ))


@router.patch("update_password",
              response=ApiResponse[StatusResponse],
              operation_id='update_password',
              auth=auth_bearer)
def update_password(request: HttpRequest, schema: UpdatePwInSchema) -> ApiResponse[StatusResponse]:
    try:
        user_email: str = sophomore_service.get_user_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    try:
        sophomore_update.change_password(email=user_email,
                                         old_password=schema.old_password,
                                         new_password=schema.new_password)
    except ServiceException as e:
        raise HttpError(
            status_code=404,
            message=e.message
        )

    return ApiResponse(data=StatusResponse(
        status="Password updated successfully"
    ))


@router.patch("update_email",
              response=ApiResponse[TokenOutSchema],
              operation_id='update_email',
              auth=auth_bearer)
def update_email(request: HttpRequest, schema: UpdateEmailInSchema) -> ApiResponse[TokenOutSchema]:
    try:
        user_email: str = sophomore_service.get_user_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    try:
        sophomore, jwt_token = sophomore_update.change_email(old_email=user_email,
                                                             new_email=schema.email,
                                                             password=schema.password)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message
        )
    return ApiResponse(data=TokenOutSchema(
        last_name=sophomore.last_name,
        first_name=sophomore.first_name,
        middle_name=sophomore.middle_name,
        email=sophomore.email,
        token=jwt_token,
    ))


@router.patch("update_credentials",
              response=ApiResponse[UpdateCredentialsOutSchema],
              operation_id='update_credentials',
              auth=auth_bearer)
def update_credentials(request: HttpRequest, schema: UpdateCredentialsInSchema) -> ApiResponse[
    UpdateCredentialsOutSchema]:
    try:
        user_email: str = sophomore_service.get_user_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    try:
        sophomore = sophomore_update.change_credentials(email=user_email,
                                                        first_name=schema.first_name,
                                                        last_name=schema.last_name,
                                                        middle_name=schema.middle_name)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message
        )
    return ApiResponse(data=SophomoreSchema(
        last_name=sophomore.last_name,
        first_name=sophomore.first_name,
        middle_name=sophomore.middle_name,
        email=sophomore.email
    ))
