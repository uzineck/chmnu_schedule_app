import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.exceptions.client import (
    ClientAlreadyExistsException,
    InsufficientPrivilegeToManageRoleException,
)
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.common.authentication.validators.exceptions import (
    InvalidPasswordPatternException,
    PasswordsNotMatchingException,
)
from core.apps.common.models import ClientRole


@pytest.fixture
def use_case(container):
    return container.resolve(CreateClientUseCase)


@pytest.fixture
def use_case_params(faker_ua, generate_email, generate_password):
    first_name = faker_ua.first_name()
    last_name = faker_ua.last_name()
    middle_name = faker_ua.middle_name()
    roles = [ClientRole.HEADMAN]
    email = generate_email()
    password = generate_password()

    return {
        "caller_roles": [ClientRole.ADMIN],
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "roles": roles,
        "email": email,
        "password": password,
        "verify_password": password,
    }


@pytest.mark.django_db
def test_create_client_success(use_case: CreateClientUseCase, use_case_params):
    RoleModelFactory(id=ClientRole.HEADMAN)
    client = use_case.execute(**use_case_params)

    assert client.first_name == use_case_params["first_name"]
    assert client.last_name == use_case_params["last_name"]
    assert client.middle_name == use_case_params["middle_name"]
    assert client.email == use_case_params["email"]
    assert ClientRole.HEADMAN in client.roles


@pytest.mark.django_db
def test_create_client_already_exists_failure(use_case: CreateClientUseCase, use_case_params):
    ClientModelFactory.create(
        first_name=use_case_params['first_name'],
        last_name=use_case_params['last_name'],
        middle_name=use_case_params['middle_name'],
        roles=[RoleModelFactory(id=ClientRole.HEADMAN)],
        email=use_case_params['email'],
        password=use_case_params['password'],
    )

    with pytest.raises(ClientAlreadyExistsException):
        use_case.execute(**use_case_params)


@pytest.mark.django_db
def test_create_client_password_validator_pattern_failure(use_case: CreateClientUseCase, use_case_params):
    use_case_params = use_case_params
    use_case_params["password"] = use_case_params["password"][:7]
    use_case_params["verify_password"] = use_case_params["password"]

    with pytest.raises(InvalidPasswordPatternException):
        use_case.execute(**use_case_params)


@pytest.mark.django_db
def test_create_client_password_validator_match_failure(
        use_case: CreateClientUseCase,
        use_case_params,
        generate_password,
):
    use_case_params = use_case_params
    use_case_params["password"] = generate_password()

    with pytest.raises(PasswordsNotMatchingException):
        use_case.execute(**use_case_params)


@pytest.mark.django_db
def test_create_client_as_client_manager_can_create_headman(use_case: CreateClientUseCase, use_case_params):
    RoleModelFactory(id=ClientRole.HEADMAN)
    use_case_params["caller_roles"] = [ClientRole.CLIENT_MANAGER]

    client = use_case.execute(**use_case_params)

    assert ClientRole.HEADMAN in client.roles


@pytest.mark.django_db
@pytest.mark.parametrize(
    "forbidden_role",
    [ClientRole.ADMIN, ClientRole.CLIENT_MANAGER, ClientRole.FACULTY_MANAGER, ClientRole.SCHEDULE_MANAGER],
)
def test_create_client_as_client_manager_cannot_create_privileged_roles(
        use_case: CreateClientUseCase,
        use_case_params,
        forbidden_role,
):
    use_case_params["caller_roles"] = [ClientRole.CLIENT_MANAGER]
    use_case_params["roles"] = [forbidden_role]

    with pytest.raises(InsufficientPrivilegeToManageRoleException):
        use_case.execute(**use_case_params)


@pytest.mark.django_db
def test_create_client_as_client_manager_cannot_mix_headman_with_privileged_role(
        use_case: CreateClientUseCase,
        use_case_params,
):
    use_case_params["caller_roles"] = [ClientRole.CLIENT_MANAGER]
    use_case_params["roles"] = [ClientRole.HEADMAN, ClientRole.ADMIN]

    with pytest.raises(InsufficientPrivilegeToManageRoleException):
        use_case.execute(**use_case_params)


@pytest.mark.django_db
def test_create_client_as_admin_can_create_any_role(use_case: CreateClientUseCase, use_case_params):
    RoleModelFactory(id=ClientRole.ADMIN)
    use_case_params["roles"] = [ClientRole.ADMIN]

    client = use_case.execute(**use_case_params)

    assert ClientRole.ADMIN in client.roles
