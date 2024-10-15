import pytest
from tests.fixtures.client.client import ClientModelFactory

from core.apps.clients.exceptions.client import ClientNotFoundException
from core.apps.clients.exceptions.issuedjwttoken import ClientTokensRevokedException
from core.apps.clients.services.client import BaseClientService
from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.clients.usecases.client.update_access_token import UpdateAccessTokenUseCase
from core.apps.common.exceptions import InvalidTokenTypeException


@pytest.fixture
def use_case(container):
    return container.resolve(UpdateAccessTokenUseCase)


@pytest.fixture(scope='function')
def use_case_params(generate_device_id):
    client = ClientModelFactory.create()
    return {
        "client": client,
    }


@pytest.mark.django_db
def test_update_access_token_success(
        use_case: UpdateAccessTokenUseCase,
        use_case_params,
        client_service: BaseClientService,
):
    tokens = client_service.generate_tokens(client=use_case_params['client'])

    new_set_of_tokens = use_case.execute(token=tokens.refresh_token)

    assert new_set_of_tokens.access_token is not None
    assert new_set_of_tokens.refresh_token is None


@pytest.mark.django_db
def test_update_access_token_type_failure(
        use_case: UpdateAccessTokenUseCase,
        use_case_params,
        client_service: BaseClientService,
):
    tokens = client_service.generate_tokens(client=use_case_params['client'])

    with pytest.raises(InvalidTokenTypeException):
        use_case.execute(token=tokens.access_token)


@pytest.mark.django_db
def test_update_access_token_client_not_found_failure(
        use_case: UpdateAccessTokenUseCase,
        use_case_params,
        client_service: BaseClientService,
):
    client = ClientModelFactory.build()
    tokens = client_service.generate_tokens(client=client)

    with pytest.raises(ClientNotFoundException):
        use_case.execute(token=tokens.refresh_token)


@pytest.mark.django_db
def test_update_access_token_refresh_revoked_failure(
        use_case: UpdateAccessTokenUseCase,
        use_case_params,
        client_service: BaseClientService,
        issued_jwt_token_service: BaseIssuedJwtTokenService,
):
    tokens = client_service.generate_tokens(client=use_case_params['client'])

    raw_tokens = [client_service.get_raw_jwt(token) for token in [tokens.access_token, tokens.refresh_token]]

    issued_jwt_token_service.bulk_create(
        subject=use_case_params['client'],
        raw_tokens=raw_tokens,
    )
    issued_jwt_token_service.revoke_client_device_tokens(
        subject=use_case_params["client"],
        device_id=client_service.get_device_id_from_token(token=tokens.refresh_token),
    )

    with pytest.raises(ClientTokensRevokedException):
        use_case.execute(token=tokens.refresh_token)
