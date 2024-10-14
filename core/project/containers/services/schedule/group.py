import punq

from core.apps.schedule.services.group import (
    BaseGroupService,
    ORMGroupService,
)
from core.apps.schedule.use_cases.group.admin_add_lesson import AdminAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.admin_remove_lesson import AdminRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.create import CreateGroupUseCase
from core.apps.schedule.use_cases.group.get_all import GetAllGroupsUseCase
from core.apps.schedule.use_cases.group.get_group_lessons import GetGroupLessonsUseCase
from core.apps.schedule.use_cases.group.get_info import GetGroupInfoUseCase
from core.apps.schedule.use_cases.group.headman_add_lesson import HeadmanAddLessonToGroupUseCase
from core.apps.schedule.use_cases.group.headman_remove_lesson import HeadmanRemoveLessonFromGroupUseCase
from core.apps.schedule.use_cases.group.update_headman import UpdateGroupHeadmanUseCase


def register_group_services(container: punq.Container):
    container.register(BaseGroupService, ORMGroupService)

    container.register(GetAllGroupsUseCase)
    container.register(CreateGroupUseCase)
    container.register(GetGroupLessonsUseCase)
    container.register(GetGroupInfoUseCase)
    container.register(UpdateGroupHeadmanUseCase)
    container.register(AdminAddLessonToGroupUseCase)
    container.register(AdminRemoveLessonFromGroupUseCase)
    container.register(HeadmanAddLessonToGroupUseCase)
    container.register(HeadmanRemoveLessonFromGroupUseCase)
