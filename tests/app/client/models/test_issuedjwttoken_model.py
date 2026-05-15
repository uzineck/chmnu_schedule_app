from django.db import IntegrityError

import pytest
import uuid
from tests.factories.client.client import ClientModelFactory
from tests.factories.client.issuedjwttoken import IssuedJwtTokenModelFactory


@pytest.mark.django_db
def test_issued_jwt_token_create():
    token = IssuedJwtTokenModelFactory.create()

    assert token.pk is not None
    assert token.jti is not None
    assert token.device_id is not None
    assert token.expiration_time is not None
    assert token.revoked is False
    assert token.created_at is not None
    assert token.updated_at is not None


@pytest.mark.django_db
def test_issued_jwt_token_revoked_defaults_false():
    token = IssuedJwtTokenModelFactory.create()

    assert token.revoked is False


@pytest.mark.django_db
def test_issued_jwt_token_jti_unique_constraint():
    fixed_jti = uuid.uuid4()
    IssuedJwtTokenModelFactory.create(jti=fixed_jti)

    with pytest.raises(IntegrityError):
        IssuedJwtTokenModelFactory.create(jti=fixed_jti)


@pytest.mark.django_db
def test_issued_jwt_token_cascade_delete():
    client = ClientModelFactory.create()
    token = IssuedJwtTokenModelFactory.create(subject=client)
    token_pk = token.pk

    client.delete()

    from core.apps.clients.models import IssuedJwtToken
    assert not IssuedJwtToken.objects.filter(pk=token_pk).exists()


@pytest.mark.django_db
def test_issued_jwt_token_str():
    token = IssuedJwtTokenModelFactory.create()

    assert str(token.jti) in str(token)
