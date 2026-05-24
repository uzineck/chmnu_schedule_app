from django.http import HttpRequest
from ninja import (
    Query,
    Router,
)

from core.api.filters import (
    PaginationIn,
    PaginationOut,
    SearchFilter,
)
from core.api.schemas import (
    ApiErrorResponse,
    ApiResponse,
    ListPaginatedResponse,
    StatusResponse,
)
from core.api.v1.clients.schemas import (
    ClientSchemaPrivate,
    RolesInSchema,
    SignUpInSchema,
    UpdatePwInAdminSchema,
)
from core.apps.clients.filters.client import ClientSearchFilter
from core.apps.clients.usecases.admin.get_all import GetAllClientsUseCase
from core.apps.clients.usecases.admin.get_list import GetClientListUseCase
from core.apps.clients.usecases.admin.update_password import UpdateClientPasswordAdminUseCase
from core.apps.clients.usecases.admin.update_role import UpdateClientRoleUseCase
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.get_info import GetClientInfoUseCase
from core.apps.common.authentication.ninja_auth import jwt_auth_client_manager
from core.apps.common.models import ClientRole
from core.project.containers.containers import get_container


router = Router(tags=["Admin"])


def _allowed_roles_for_caller(caller_roles: list[ClientRole]) -> tuple[ClientRole, ...] | None:
    """Admin sees every client; everyone else (CLIENT_MANAGER) is scoped to
    HEADMAN."""
    if ClientRole.ADMIN in caller_roles:
        return None
    return (ClientRole.HEADMAN,)


@router.get(
    "",
    response={
        200: ApiResponse[ListPaginatedResponse[ClientSchemaPrivate]],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
    },
    operation_id='get_client_list',
    auth=jwt_auth_client_manager,
    summary="Admin: search and paginate clients",
    description=(
        "Returns a paginated list of clients. `search` matches against email, first name, last "
        "name, and middle name (case-insensitive). ADMIN sees every client; CLIENT_MANAGER only "
        "sees clients with the HEADMAN role."
    ),
)
def get_client_list(
        request: HttpRequest,
        filters: Query[SearchFilter],
        pagination_in: Query[PaginationIn],
) -> ApiResponse[ListPaginatedResponse[ClientSchemaPrivate]]:
    container = get_container()
    use_case: GetClientListUseCase = container.resolve(GetClientListUseCase)
    domain_filter = ClientSearchFilter(
        search=filters.search,
        allowed_roles=_allowed_roles_for_caller(request.client_roles),
    )
    item_list, item_count = use_case.execute(filters=domain_filter, pagination_in=pagination_in)
    pagination_out = PaginationOut(
        offset=pagination_in.offset,
        limit=pagination_in.limit,
        total=item_count,
    )

    return ApiResponse(
        data=ListPaginatedResponse(
            items=[ClientSchemaPrivate.from_entity(obj) for obj in item_list],
            pagination=pagination_out,
        ),
    )


@router.get(
    "all",
    response={
        200: ApiResponse[list[ClientSchemaPrivate]],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
    },
    operation_id='get_all_clients',
    auth=jwt_auth_client_manager,
    summary="Admin: list every visible client",
    description=(
        "Returns the full collection of clients visible to the caller. ADMIN gets every client; "
        "CLIENT_MANAGER gets only HEADMAN clients. Intended for dropdowns; use `get_client_list` "
        "for paginated / searchable access."
    ),
)
def get_all_clients(request: HttpRequest) -> ApiResponse[list[ClientSchemaPrivate]]:
    container = get_container()
    use_case: GetAllClientsUseCase = container.resolve(GetAllClientsUseCase)
    domain_filter = ClientSearchFilter(
        allowed_roles=_allowed_roles_for_caller(request.client_roles),
    )
    items = [ClientSchemaPrivate.from_entity(obj) for obj in use_case.execute(filters=domain_filter)]
    return ApiResponse(
        data=items,
    )


@router.get(
    "{client_email}/info",
    response={
        200: ApiResponse[ClientSchemaPrivate],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='get_client_info_admin',
    auth=jwt_auth_client_manager,
    summary="Admin: get a client's profile",
    description="Returns the full profile for any client by email. Requires ADMIN or CLIENT_MANAGER role.",
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
    response={
        201: ApiResponse[ClientSchemaPrivate],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        409: ApiErrorResponse,
    },
    operation_id='sign_up',
    auth=jwt_auth_client_manager,
    summary="Admin: register a new client",
    description=(
        "Creates a new client with the supplied roles and credentials. `password` must equal "
        "`verify_password` and meet the password policy. Returns 409 if the email is already taken. "
        "ADMIN can assign any role; CLIENT_MANAGER may only create HEADMAN clients and gets 403 "
        "otherwise. Requires ADMIN or CLIENT_MANAGER role."
    ),
)
def sign_up(
        request: HttpRequest,
        schema: SignUpInSchema,
) -> tuple[int, ApiResponse[ClientSchemaPrivate]]:
    container = get_container()
    use_case: CreateClientUseCase = container.resolve(CreateClientUseCase)
    client = use_case.execute(
        caller_roles=request.client_roles,
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
        roles=schema.roles,
        email=schema.email,
        password=schema.password,
        verify_password=schema.verify_password,
    )

    return 201, ApiResponse(
        data=ClientSchemaPrivate.from_entity(client=client),
    )


@router.patch(
    "{client_email}/update_password",
    response={
        200: ApiResponse[StatusResponse],
        400: ApiErrorResponse,
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='update_password_admin',
    auth=jwt_auth_client_manager,
    summary="Admin: reset a client's password",
    description=(
        "Sets a new password for the target client without requiring the old one. `new_password` "
        "must equal `verify_password`. Requires ADMIN or CLIENT_MANAGER role."
    ),
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
    response={
        200: ApiResponse[ClientSchemaPrivate],
        401: ApiErrorResponse,
        403: ApiErrorResponse,
        404: ApiErrorResponse,
    },
    operation_id='update_client_roles',
    auth=jwt_auth_client_manager,
    summary="Admin: replace a client's roles",
    description=(
        "Replaces the target client's full role set with the supplied list. Sending an empty list "
        "strips all permissions. Requires ADMIN or CLIENT_MANAGER role."
    ),
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
