import punq

from core.apps.schedule.services.group import (
    BaseGroupService,
    ORMGroupService,
)
from core.apps.schedule.use_cases.group.admin_add_lesson_to_group import AdminAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.admin_remove_lesson_from_group import AdminRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.create_group import CreateGroupUseCase
from core.apps.schedule.use_cases.group.get_group_info import GetGroupInfoUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.headman_add_lesson_to_group import HeadmanAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.headman_remove_lesson_from_group import HeadmanRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase


def register_group_services(container: punq.Container):
    container.register(BaseGroupService, ORMGroupService)

    container.register(CreateGroupUseCase)
    container.register(GetGroupInfoUseCase)
    container.register(GetGroupLessonsUseCase)
    container.register(UpdateGroupHeadmanUseCase)
    container.register(AdminAddLessonToGroupUseCase)
    container.register(AdminRemoveLessonFromGroupUseCase)
    container.register(HeadmanAddLessonToGroupUseCase)
    container.register(HeadmanRemoveLessonFromGroupUseCase)
