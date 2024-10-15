from collections.abc import Iterable
from dataclasses import dataclass

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService


@dataclass
class GetSubjectListUseCase:
    subject_service: BaseSubjectService

    def execute(self, filters: SearchFilter, pagination: PaginationIn) -> tuple[Iterable[SubjectEntity], int]:
        subject_list = self.subject_service.get_list(filters=filters, pagination=pagination)
        subject_count = self.subject_service.get_count(filters=filters)

        return subject_list, subject_count
