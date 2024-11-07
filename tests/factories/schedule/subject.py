import factory
import uuid
from factory.django import DjangoModelFactory
from faker import Faker
from transliterate import slugify

from core.apps.schedule.models import Subject


class SubjectModelFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    subject_uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    title = factory.LazyFunction(lambda: f'{Faker("uk_UA").text(max_nb_chars=15)}')
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = Subject
