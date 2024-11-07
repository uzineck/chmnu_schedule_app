import factory
import uuid
from factory.django import DjangoModelFactory
from faker import Faker

from core.apps.schedule.models import Room


faker = Faker()


class RoomModelFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    room_uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    number = factory.LazyFunction(lambda: RoomModelFactory.generate_custom_number())
    description = None

    @staticmethod
    def generate_custom_number():
        """Generates a random number in one of the specified formats."""
        pattern = faker.random_element(['XXX', 'XXX-X', 'X-XXX'])

        if pattern == 'XXX':
            return f"{faker.random_number(digits=3, fix_len=True)}"
        elif pattern == 'XXX-X':
            return f"{faker.random_number(digits=3, fix_len=True)}-{faker.random_number(digits=1)}"
        elif pattern == 'X-XXX':
            return f"{faker.random_number(digits=1)}-{faker.random_number(digits=3, fix_len=True)}"

    class Meta:
        model = Room
