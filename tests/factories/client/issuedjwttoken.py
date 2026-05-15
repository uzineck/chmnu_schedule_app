import factory
import uuid
from datetime import (
    datetime,
    timezone,
)
from factory.django import DjangoModelFactory
from tests.factories.client.client import ClientModelFactory

from core.apps.clients.models import IssuedJwtToken


class IssuedJwtTokenModelFactory(DjangoModelFactory):
    subject = factory.SubFactory(ClientModelFactory)
    jti = factory.LazyFunction(uuid.uuid4)
    device_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    expiration_time = factory.LazyFunction(
        lambda: int(datetime.now(tz=timezone.utc).timestamp()) + 3600,
    )
    revoked = False

    class Meta:
        model = IssuedJwtToken
