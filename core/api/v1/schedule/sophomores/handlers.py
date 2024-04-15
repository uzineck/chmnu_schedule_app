from django.http import HttpRequest
from ninja import Router

from core.api.schemas import ApiResponse
from core.api.v1.schedule.sophomores.schemas import SignUpInSchema, SignUpOutSchema, LogInOutSchema, LogInSchema
from core.api.v1.schedule.sophomores.containers import sophomore_auth

router = Router(tags=["Sophomores"])


@router.post("sign_up", response=ApiResponse[SignUpOutSchema], operation_id='sign_up')
def sign_up_handler(request: HttpRequest, schema: SignUpInSchema) -> ApiResponse[SignUpOutSchema]:
    sophomore = sophomore_auth.sign_up(first_name=schema.first_name,
                                       last_name=schema.last_name,
                                       middle_name=schema.middle_name,
                                       email=schema.email,
                                       password=schema.password)
    return ApiResponse(data=SignUpOutSchema(
        sophomore=sophomore
    ))


@router.post("login", response=ApiResponse[LogInOutSchema], operation_id='login')
def login_handler(request: HttpRequest, schema: LogInSchema) -> ApiResponse[LogInOutSchema]:
    jwt_token = sophomore_auth.login(email=schema.email, password=schema.password)
    return ApiResponse(data=LogInOutSchema(
        token=jwt_token
    ))
