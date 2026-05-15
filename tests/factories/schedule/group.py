import factory
import uuid
from factory.django import DjangoModelFactory
from tests.factories.schedule.faculty import FacultyModelFactory

from core.apps.schedule.models import Group


class GroupModelFactory(DjangoModelFactory):
    group_uuid = factory.LazyFunction(uuid.uuid4)
    number = factory.Sequence(lambda n: f"ПМ-{n:03}")
    faculty = factory.SubFactory(FacultyModelFactory)
    has_subgroups = True
    headman = None

    class Meta:
        model = Group
