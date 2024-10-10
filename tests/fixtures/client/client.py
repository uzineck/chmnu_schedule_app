import factory
from factory.django import DjangoModelFactory
from tests.fixtures.client.utils import generate_email

from core.apps.clients.models import Client
from core.apps.common.models import ClientRole


class ClientModelFactory(DjangoModelFactory):
    first_name = factory.Faker('first_name', locale='uk_UA')
    last_name = factory.Faker('last_name', locale='uk_UA')
    middle_name = factory.Faker('middle_name', locale='uk_UA')
    role = factory.Iterator(ClientRole)
    email = generate_email()
    password = factory.Faker('password')

    class Meta:
        model = Client


