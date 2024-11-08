import pytest
from tests.factories.schedule.faculty import FacultyModelFactory
from tests.factories.schedule.lesson import LessonModelFactory
from tests.factories.schedule.room import RoomModelFactory
from tests.factories.schedule.subject import SubjectModelFactory
from tests.factories.schedule.teacher import TeacherModelFactory
from tests.factories.schedule.timeslot import TimeslotModelFactory

from core.apps.schedule.services.faculty import BaseFacultyService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.services.room import BaseRoomService
from core.apps.schedule.services.subject import BaseSubjectService
from core.apps.schedule.services.teacher import BaseTeacherService
from core.apps.schedule.services.timeslot import BaseTimeslotService


@pytest.fixture
def subject_service(container) -> BaseSubjectService:
    return container.resolve(BaseSubjectService)


@pytest.fixture
def room_service(container) -> BaseRoomService:
    return container.resolve(BaseRoomService)


@pytest.fixture
def teacher_service(container) -> BaseTeacherService:
    return container.resolve(BaseTeacherService)


@pytest.fixture
def faculty_service(container) -> BaseFacultyService:
    return container.resolve(BaseFacultyService)


@pytest.fixture
def timeslot_service(container) -> BaseTimeslotService:
    return container.resolve(BaseTimeslotService)


@pytest.fixture
def lesson_service(container) -> BaseLessonService:
    return container.resolve(BaseLessonService)


@pytest.fixture(scope='function')
def subject_create_batch():
    def _subject_create_batch(size: int, **kwargs) -> list:
        return SubjectModelFactory.create_batch(size=size, **kwargs)

    return _subject_create_batch


@pytest.fixture(scope='function')
def room_create_batch():
    def _room_create_batch(size: int, **kwargs) -> list:
        return RoomModelFactory.create_batch(size=size, **kwargs)

    return _room_create_batch


@pytest.fixture(scope='function')
def teacher_create_batch():
    def _teacher_create_batch(size: int, **kwargs) -> list:
        return TeacherModelFactory.create_batch(size=size, **kwargs)

    return _teacher_create_batch


@pytest.fixture(scope='function')
def faculty_create_batch():
    def _faculty_create_batch(size: int, **kwargs) -> list:
        return FacultyModelFactory.create_batch(size=size, **kwargs)

    return _faculty_create_batch


@pytest.fixture(scope='function')
def timeslot_create_batch():
    def _timeslot_create_batch(size: int, **kwargs) -> list:
        return TimeslotModelFactory.create_batch(size=size, **kwargs)

    return _timeslot_create_batch


@pytest.fixture(scope='function')
def lesson_create_batch():
    def _lesson_create_batch(size: int, **kwargs) -> list:
        return LessonModelFactory.create_batch(size=size, **kwargs)

    return _lesson_create_batch


@pytest.fixture(scope='function')
def subject_create():
    def _subject_create(**kwargs):
        return SubjectModelFactory.create(**kwargs)

    return _subject_create


@pytest.fixture(scope='function')
def room_create():
    def _room_create(**kwargs):
        return RoomModelFactory.create(**kwargs)

    return _room_create


@pytest.fixture(scope='function')
def teacher_create():
    def _teacher_create(**kwargs):
        return TeacherModelFactory.create(**kwargs)

    return _teacher_create


@pytest.fixture(scope='function')
def faculty_create():
    def _faculty_create(**kwargs):
        return FacultyModelFactory.create(**kwargs)

    return _faculty_create


@pytest.fixture(scope='function')
def timeslot_create():
    def _timeslot_create(**kwargs):
        return TimeslotModelFactory.create(**kwargs)

    return _timeslot_create


@pytest.fixture(scope='function')
def lesson_create():
    def _lesson_create(**kwargs):
        return LessonModelFactory.create(**kwargs)

    return _lesson_create


@pytest.fixture(scope='function')
def subject_build():
    def _subject_build(**kwargs):
        return SubjectModelFactory.build(**kwargs)

    return _subject_build


@pytest.fixture(scope='function')
def room_build():
    def _room_build(**kwargs):
        return RoomModelFactory.build(**kwargs)

    return _room_build


@pytest.fixture(scope='function')
def teacher_build():
    def _teacher_build(**kwargs):
        return TeacherModelFactory.build(**kwargs)

    return _teacher_build


@pytest.fixture(scope='function')
def faculty_build():
    def _faculty_build(**kwargs):
        return FacultyModelFactory.build(**kwargs)

    return _faculty_build


@pytest.fixture(scope='function')
def timeslot_build():
    def _timeslot_build(**kwargs):
        return TimeslotModelFactory.build(**kwargs)

    return _timeslot_build


@pytest.fixture(scope='function')
def lesson_build():
    def _lesson_build(**kwargs):
        return LessonModelFactory.build(**kwargs)

    return _lesson_build
