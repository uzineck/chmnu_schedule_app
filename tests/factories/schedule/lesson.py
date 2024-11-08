import factory
import uuid
from factory.django import DjangoModelFactory
from tests.factories.schedule.room import RoomModelFactory
from tests.factories.schedule.subject import SubjectModelFactory
from tests.factories.schedule.teacher import TeacherModelFactory
from tests.factories.schedule.timeslot import TimeslotModelFactory

from core.apps.common.models import LessonType
from core.apps.schedule.models import Lesson


class LessonModelFactory(DjangoModelFactory):
    id = factory.Sequence(lambda n: n)
    lesson_uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    type = factory.Iterator(LessonType)
    subject = factory.SubFactory(SubjectModelFactory)
    teacher = factory.SubFactory(TeacherModelFactory)
    room = factory.SubFactory(RoomModelFactory)
    timeslot = factory.SubFactory(TimeslotModelFactory)

    class Meta:
        model = Lesson
