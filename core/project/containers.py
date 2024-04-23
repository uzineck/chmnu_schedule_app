from functools import lru_cache

import punq


from core.apps.clients.services.auth import BaseAuthService, AuthService
from core.apps.clients.services.sophomore import BaseSophomoreService, ORMSophomoreService
from core.apps.clients.services.update import BaseUpdateUserService, UpdateUserService
from core.apps.common.authentication.password import BasePasswordService, BcryptPasswordService
from core.apps.common.authentication.token import BaseTokenService, JWTTokenService
from core.apps.schedule.services.groups import BaseGroupService, ORMGroupService
from core.apps.schedule.services.lessons import BaseLessonService, ORMLessonService
from core.apps.schedule.services.rooms import BaseRoomService, ORMRoomService
from core.apps.schedule.services.subjects import BaseSubjectService, ORMSubjectService
from core.apps.schedule.services.teachers import BaseTeacherService, ORMTeacherService
from core.apps.schedule.services.timeslots import BaseTimeslotService, ORMTimeslotService
from core.apps.schedule.use_cases.lessons.create import CreateLessonUseCase


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()
    # Client containers
    container.register(BaseSophomoreService, ORMSophomoreService)
    container.register(BasePasswordService, BcryptPasswordService)
    container.register(BaseTokenService, JWTTokenService)
    container.register(BaseAuthService, AuthService)
    container.register(BaseUpdateUserService, UpdateUserService)

    # Subject containers
    container.register(BaseSubjectService, ORMSubjectService)

    # Room containers
    container.register(BaseRoomService, ORMRoomService)

    # Timeslot containers
    container.register(BaseTimeslotService, ORMTimeslotService)

    # Teacher containers
    container.register(BaseTeacherService, ORMTeacherService)

    # Lesson containers
    container.register(BaseLessonService, ORMLessonService)
    container.register(CreateLessonUseCase)

    # Group containers
    container.register(BaseGroupService, ORMGroupService)

    return container


