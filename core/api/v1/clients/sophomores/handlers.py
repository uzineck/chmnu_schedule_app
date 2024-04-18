from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from core.api.schemas import ApiResponse
from core.api.v1.clients.sophomores.schemas import SignUpInSchema, SignUpOutSchema, LogInOutSchema, LogInSchema, \
    UpdateEmailInSchema, UpdateEmailOutSchema, UpdatePwInSchema, UpdatePwOutSchema, UpdateCredentialsInSchema, \
    UpdateCredentialsOutSchema
from core.api.v1.clients.sophomores.containers import sophomore_auth, sophomore_service, sophomore_update
from core.apps.common.authentication import auth_bearer
from core.apps.common.exceptions import ServiceException, JWTKeyParsingException

router = Router(tags=["Sophomores"])


@router.post("sign_up", response=ApiResponse[SignUpOutSchema], operation_id='sign_up')
def sign_up_handler(request: HttpRequest, schema: SignUpInSchema) -> ApiResponse[SignUpOutSchema]:
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

    return ApiResponse(data=SignUpOutSchema(
        greetings=f"You have successfully signed up "
                  f"{sophomore.last_name} {sophomore.first_name[0]}. {sophomore.middle_name[0]}."
    ))


@router.post("login", response=ApiResponse[LogInOutSchema], operation_id='login')
def login_handler(request: HttpRequest, schema: LogInSchema) -> ApiResponse[LogInOutSchema]:
    try:
        jwt_token = sophomore_auth.login(email=schema.email, password=schema.password)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message
        )
    return ApiResponse(data=LogInOutSchema(
        token=jwt_token
    ))


@router.patch("password",
              response=ApiResponse[UpdatePwOutSchema],
              operation_id='update_password',
              auth=auth_bearer)
def update_password(request: HttpRequest, schema: UpdatePwInSchema) -> ApiResponse[UpdatePwOutSchema]:
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

    return ApiResponse(data=UpdatePwOutSchema(
        status="Password updated successfully"
    ))


@router.patch("email",
              response=ApiResponse[UpdateEmailOutSchema],
              operation_id='update_email',
              auth=auth_bearer)
def update_email(request: HttpRequest, schema: UpdateEmailInSchema) -> ApiResponse[UpdateEmailOutSchema]:
    try:
        user_email: str = sophomore_service.get_user_email_from_token(token=request.auth)
    except JWTKeyParsingException as e:
        raise HttpError(
            status_code=401,
            message=e.message
        )

    try:
        email, token = sophomore_update.change_email(old_email=user_email,
                                                     new_email=schema.email,
                                                     password=schema.password)
    except ServiceException as e:
        raise HttpError(
            status_code=400,
            message=e.message
        )
    return ApiResponse(data=UpdateEmailOutSchema(
        email=f"Email changed successfully: {email}",
        token=token
    ))


@router.patch("credentials",
              response=ApiResponse[UpdateCredentialsOutSchema],
              operation_id='update_credentials',
              auth=auth_bearer)
def update_credentials(request: HttpRequest, schema: UpdateCredentialsInSchema) -> ApiResponse[UpdateCredentialsOutSchema]:
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
    return ApiResponse(data=UpdateCredentialsOutSchema(
        sophomore=f"Sophomore updated successfully: {sophomore.last_name} {sophomore.first_name[0]}. "
                  f"{sophomore.middle_name[0]}."
    ))
