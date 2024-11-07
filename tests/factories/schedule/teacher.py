import factory
import uuid
from factory.django import DjangoModelFactory

from core.apps.common.models import TeachersDegree
from core.apps.schedule.models import Teacher


class TeacherModelFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    teacher_uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    first_name = factory.Faker('first_name', locale='uk_UA')
    last_name = factory.Faker('last_name', locale='uk_UA')
    middle_name = factory.Faker('middle_name', locale='uk_UA')
    rank = factory.Iterator(TeachersDegree)
    is_active = True

    class Meta:
        model = Teacher
