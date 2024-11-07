import pytest

from core.apps.schedule.services.faculty import BaseFacultyService
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
