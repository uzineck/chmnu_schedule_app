import factory
from factory.django import DjangoModelFactory
from tests.factories.schedule.group import GroupModelFactory
from tests.factories.schedule.lesson import LessonModelFactory

from core.apps.schedule.models import GroupLesson


class GroupLessonModelFactory(DjangoModelFactory):
    group = factory.SubFactory(GroupModelFactory)
    lesson = factory.SubFactory(LessonModelFactory)
    subgroup = None

    class Meta:
        model = GroupLesson
