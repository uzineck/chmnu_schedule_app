import pytest
from tests.factories.client.client import ClientModelFactory

from core.apps.common.authentication.token import BaseTokenService
from core.apps.common.models import TokenType


@pytest.fixture(scope='function')
def service_params(generate_device_id):
    client = ClientModelFactory.build()
    payload = {"device_id": generate_device_id}

    return {
        "client": client,
        "payload": payload,
    }


def test_create_access_token(token_service: BaseTokenService, service_params, get_current_timestamp):
    access_token = token_service.create_access_token(**service_params)

    assert token_service.get_token_type_from_token(token=access_token) == TokenType.ACCESS
    assert token_service.get_device_id_from_token(token=access_token) == service_params['payload']['device_id']
    assert token_service.get_client_role_from_token(token=access_token) == service_params['client'].role
    assert token_service.get_client_email_from_token(token=access_token) == service_params['client'].email
    assert token_service.get_expiration_time_from_token(token=access_token) > get_current_timestamp


def test_create_refresh_token(
        token_service: BaseTokenService,
        service_params,
        get_current_timestamp,
):
    refresh_token = token_service.create_refresh_token(**service_params)

    assert token_service.get_token_type_from_token(token=refresh_token) == TokenType.REFRESH
    assert token_service.get_device_id_from_token(token=refresh_token) == service_params['payload']['device_id']
    assert token_service.get_client_role_from_token(token=refresh_token) == service_params['client'].role
    assert token_service.get_client_email_from_token(token=refresh_token) == service_params['client'].email
    assert token_service.get_expiration_time_from_token(token=refresh_token) > get_current_timestamp


def test_get_raw_jwt_payload(token_service: BaseTokenService, service_params):
    access_token = token_service.create_access_token(**service_params)
    payload = token_service.get_raw_jwt(token=access_token)

    assert payload["exp"] == token_service.get_expiration_time_from_token(token=access_token)
    assert payload["type"] == token_service.get_token_type_from_token(token=access_token)
    assert payload["sub"] == service_params['client'].email
    assert payload["client_email"] == service_params['client'].email
    assert payload["client_role"] == service_params['client'].role
    assert payload["device_id"] == service_params['payload']['device_id']
    assert payload["iat"] <= token_service.get_expiration_time_from_token(token=access_token)
