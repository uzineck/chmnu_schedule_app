import jwt
import pytest
import uuid
from datetime import (
    datetime,
    timezone,
)
from ninja.errors import HttpError

from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.apps.common.authentication.auth_check import AuthCheck
from core.apps.common.authentication.bearer import JWTBearer
from core.apps.common.authentication.token import (
    BaseTokenService,
    JWTTokenService,
)
from core.apps.common.exceptions import JWTKeyParsingException
from core.apps.common.factory import convert_to_timestamp
from core.apps.common.models import (
    ClientRole,
    TokenType,
)


def _now_ts() -> int:
    return convert_to_timestamp(datetime.now(tz=timezone.utc))


def _signed(payload: dict, key: str = None) -> str:
    return jwt.encode(
        payload=payload,
        key=key if key is not None else JWTTokenService.JWT_SECRET_KEY,
        algorithm=JWTTokenService.ALGORITHM,
    )


@pytest.mark.django_db
def test_authenticate_valid_token_attaches_request_attrs(
        mock_request,
        valid_access_token,
):
    client_entity, token = valid_access_token(role=ClientRole.HEADMAN)
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    returned = auth.authenticate(request=mock_request, token=token)

    assert returned == token
    assert mock_request.client_email == client_entity.email
    assert mock_request.client_roles == [ClientRole.HEADMAN]
    assert mock_request.token_jti is not None
    assert mock_request.device_id is not None
    assert mock_request.token_expiration > _now_ts()


@pytest.mark.django_db
def test_authenticate_malformed_token_raises_401(mock_request):
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token="not.a.real.jwt")

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Invalid token"


@pytest.mark.django_db
def test_authenticate_expired_token_raises_401(
        mock_request,
        token_service: BaseTokenService,
        client_with_role,
):
    _, client_entity = client_with_role(ClientRole.HEADMAN)
    past = _now_ts() - 3600
    token = token_service.create_access_token(
        client=client_entity,
        payload={"device_id": str(uuid.uuid4()), "nbf": past},
    )
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token=token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Invalid token"


@pytest.mark.django_db
def test_authenticate_wrong_signature_raises_401(mock_request):
    now = _now_ts()
    token = _signed(
        payload={
            "type": TokenType.ACCESS.value,
            "exp": now + 600,
            "iat": now,
            "nbf": now,
            "jti": str(uuid.uuid4()),
        },
        key="totally_different_secret",
    )
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token=token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Invalid token"


@pytest.mark.django_db
def test_authenticate_missing_required_claim_raises_401(mock_request):
    now = _now_ts()
    token = _signed(payload={
        "exp": now + 600,
        "iat": now,
        "nbf": now,
        "jti": str(uuid.uuid4()),
    })
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token=token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Invalid token"


@pytest.mark.django_db
def test_authenticate_refresh_token_used_as_access_raises_401(
        mock_request,
        token_service: BaseTokenService,
        client_with_role,
        generate_device_id,
):
    _, client_entity = client_with_role(ClientRole.HEADMAN)
    refresh_token = token_service.create_refresh_token(
        client=client_entity,
        payload={"device_id": generate_device_id},
    )
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token=refresh_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Invalid token type"


@pytest.mark.django_db
def test_authenticate_revoked_token_raises_401(
        mock_request,
        valid_access_token,
        issued_jwt_token_service: BaseIssuedJwtTokenService,
        token_service: BaseTokenService,
):
    client_entity, token = valid_access_token(role=ClientRole.HEADMAN)
    payload = token_service.decode_token(token=token)
    issued_jwt_token_service.bulk_create(subject=client_entity, raw_tokens=[payload])
    issued_jwt_token_service.revoke_client_tokens(subject=client_entity)

    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token=token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Revoked token"


@pytest.mark.django_db
def test_authenticate_role_not_allowed_raises_403(mock_request, valid_access_token):
    client_entity, token = valid_access_token(role=ClientRole.HEADMAN)
    auth = AuthCheck(allowed_roles=[ClientRole.ADMIN])

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token=token)

    assert exc_info.value.status_code == 403


@pytest.mark.django_db
def test_authenticate_email_not_in_allowed_emails_raises_403(
        mock_request,
        valid_access_token,
):
    client_entity, token = valid_access_token(role=ClientRole.HEADMAN)
    auth = AuthCheck(
        allowed_roles=[ClientRole.HEADMAN],
        allowed_emails=["someone-else@gmail.com"],
    )

    with pytest.raises(HttpError) as exc_info:
        auth.authenticate(request=mock_request, token=token)

    assert exc_info.value.status_code == 403


@pytest.mark.django_db
def test_authenticate_allowed_emails_match_succeeds(
        mock_request,
        valid_access_token,
):
    client_entity, token = valid_access_token(role=ClientRole.HEADMAN)
    auth = AuthCheck(
        allowed_roles=[ClientRole.HEADMAN],
        allowed_emails=[client_entity.email],
    )

    auth.authenticate(request=mock_request, token=token)

    assert mock_request.client_email == client_entity.email


@pytest.mark.django_db
def test_authenticate_missing_client_email_in_payload_raises_jwt_parsing(mock_request):
    now = _now_ts()
    token = _signed(payload={
        "type": TokenType.ACCESS.value,
        "exp": now + 600,
        "iat": now,
        "nbf": now,
        "jti": str(uuid.uuid4()),
        "client_roles": [ClientRole.HEADMAN.value],
    })
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(JWTKeyParsingException):
        auth.authenticate(request=mock_request, token=token)


@pytest.mark.django_db
def test_authenticate_missing_client_roles_in_payload_raises_jwt_parsing(mock_request):
    now = _now_ts()
    token = _signed(payload={
        "type": TokenType.ACCESS.value,
        "exp": now + 600,
        "iat": now,
        "nbf": now,
        "jti": str(uuid.uuid4()),
        "client_email": "ghost@gmail.com",
    })
    auth = AuthCheck(allowed_roles=[ClientRole.HEADMAN])

    with pytest.raises(JWTKeyParsingException):
        auth.authenticate(request=mock_request, token=token)


@pytest.mark.django_db
def test_jwt_bearer_inherits_authenticate(mock_request, valid_access_token):
    client_entity, token = valid_access_token(role=ClientRole.HEADMAN)
    bearer = JWTBearer(allowed_roles=[ClientRole.HEADMAN])

    returned = bearer.authenticate(request=mock_request, token=token)

    assert returned == token
    assert mock_request.client_email == client_entity.email
