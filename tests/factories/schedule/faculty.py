import factory
import uuid
from factory.django import DjangoModelFactory
from faker import Faker

from core.apps.schedule.models import Faculty


class FacultyModelFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    faculty_uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.LazyFunction(lambda: f'{Faker("uk_UA").text(max_nb_chars=50)}')
    code_name = factory.LazyAttribute(lambda obj: ''.join(word[0] for word in obj.name.split()))

    class Meta:
        model = Faculty
