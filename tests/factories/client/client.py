import factory
from factory.django import DjangoModelFactory
from faker import Faker
from tests.factories.client.role import RoleModelFactory

from core.apps.clients.models import Client
from core.apps.common.models import ClientRole


class ClientModelFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    first_name = factory.Faker('first_name', locale='uk_UA')
    last_name = factory.Faker('last_name', locale='uk_UA')
    middle_name = factory.Faker('middle_name', locale='uk_UA')
    email = factory.LazyFunction(lambda: f'{Faker().user_name()}@gmail.com')
    password = factory.Faker('password')

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for role in extracted:
                self.roles.add(role)
        else:
            self.roles.add(RoleModelFactory(id=ClientRole.DEFAULT))

    class Meta:
        model = Client
