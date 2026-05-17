from dataclasses import dataclass

from core.apps.common.cache.decorator import cache_decorator
from core.apps.common.cache.timeouts import Timeout
from core.apps.schedule.entities.group import Group as GroupEntity
from core.apps.schedule.entities.views import LessonForGroupView
from core.apps.schedule.filters.group import LessonFilter
from core.apps.schedule.services.group import BaseGroupService
from core.apps.schedule.services.lesson import BaseLessonService
from core.apps.schedule.validators.uuid_validator import BaseUuidValidatorService


@dataclass
class GetGroupLessonsUseCase:
    group_service: BaseGroupService
    lesson_service: BaseLessonService

    uuid_validator_service: BaseUuidValidatorService

    @cache_decorator.get_or_set_cache(
        model_prefix='group',
        identifier=lambda kw: kw['group_uuid'],
        func_prefix='lessons',
        timeout=Timeout.HALF_DAY,
    )
    def execute(self, group_uuid: str, filters: LessonFilter) -> tuple[GroupEntity, list[LessonForGroupView]]:
        self.uuid_validator_service.validate(uuid_str=group_uuid)

        group = self.group_service.get_by_uuid(group_uuid=group_uuid)

        if filters.subgroup is not None:
            self.group_service.validate_subgroup_for_group(group=group, subgroup=filters.subgroup)

        views = self.lesson_service.get_lessons_with_subgroups_for_group(group_id=group.id, filter_query=filters)
        return group, views
