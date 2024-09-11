import punq
from functools import lru_cache

from core.apps.clients.services.client import (
    BaseClientService,
    ORMClientService,
)
from core.apps.clients.usecases.client.create import CreateClientUseCase
from core.apps.clients.usecases.client.login import LoginClientUseCase
from core.apps.clients.usecases.client.update_credentials import UpdateClientCredentialsUseCase
from core.apps.clients.usecases.client.update_email import UpdateClientEmailUseCase
from core.apps.clients.usecases.client.update_password import UpdateClientPasswordUseCase
from core.apps.clients.usecases.client.update_role import UpdateClientRoleUseCase
from core.apps.clients.usecases.headman.get_headman_info import GetHeadmanInfoUseCase
from core.apps.common.authentication.password import (
    BasePasswordService,
    BcryptPasswordService,
)
from core.apps.common.authentication.token import (
    BaseTokenService,
    JWTTokenService,
)
from core.apps.schedule.services.groups import (
    BaseGroupService,
    ORMGroupService,
)
from core.apps.schedule.services.lessons import (
    BaseLessonService,
    ORMLessonService,
)
from core.apps.schedule.services.rooms import (
    BaseRoomService,
    ORMRoomService,
)
from core.apps.schedule.services.subjects import (
    BaseSubjectService,
    ORMSubjectService,
)
from core.apps.schedule.services.teachers import (
    BaseTeacherService,
    ORMTeacherService,
)
from core.apps.schedule.services.timeslots import (
    BaseTimeslotService,
    ORMTimeslotService,
)
from core.apps.schedule.use_cases.group.add_lesson_to_group import AddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.create_group import CreateGroupUseCase
from core.apps.schedule.use_cases.group.get_group_info import GetGroupInfoUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.remove_lesson_from_group import RemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase
from core.apps.schedule.use_cases.lessons.create import CreateLessonUseCase
from core.apps.schedule.use_cases.teacher.get_lessons_for_teacher import GetLessonsForTeacherUseCase


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()
    # Client containers
    container.register(BaseClientService, ORMClientService)
    container.register(BasePasswordService, BcryptPasswordService)
    container.register(BaseTokenService, JWTTokenService)
    container.register(CreateClientUseCase)
    container.register(LoginClientUseCase)
    container.register(UpdateClientEmailUseCase)
    container.register(UpdateClientPasswordUseCase)
    container.register(UpdateClientCredentialsUseCase)
    container.register(UpdateClientRoleUseCase)
    container.register(GetHeadmanInfoUseCase)

    # Subject containers
    container.register(BaseSubjectService, ORMSubjectService)

    # Room containers
    container.register(BaseRoomService, ORMRoomService)

    # Timeslot containers
    container.register(BaseTimeslotService, ORMTimeslotService)

    # Teacher containers
    container.register(BaseTeacherService, ORMTeacherService)
    container.register(GetLessonsForTeacherUseCase)

    # Lesson containers
    container.register(BaseLessonService, ORMLessonService)
    container.register(CreateLessonUseCase)

    # Group containers
    container.register(BaseGroupService, ORMGroupService)
    container.register(CreateGroupUseCase)
    container.register(GetGroupInfoUseCase)
    container.register(GetGroupLessonsUseCase)
    container.register(UpdateGroupHeadmanUseCase)
    container.register(AddLessonToGroupUseCase)
    container.register(RemoveLessonFromGroupUseCase)

    return container


