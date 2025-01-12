import pytest
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.exceptions.client import ClientAlreadyExistsException
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.common.authentication.validators.exceptions import (
    InvalidEmailPatternException,
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
    client = use_case.execute(**use_case_params)

    assert client.first_name == use_case_params["first_name"]
    assert client.last_name == use_case_params["last_name"]
    assert client.middle_name == use_case_params["middle_name"]
    assert client.email == use_case_params["email"]


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
def test_create_client_email_validator_failure(use_case: CreateClientUseCase, use_case_params, faker):
    use_case_params = use_case_params
    use_case_params['email'] = faker.email()

    with pytest.raises(InvalidEmailPatternException):
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
