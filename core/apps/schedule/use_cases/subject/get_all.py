from dataclasses import dataclass
from typing import Iterable

from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService


@dataclass
class GetAllSubjectsUseCase:
    subject_service: BaseSubjectService

    def execute(self) -> Iterable[SubjectEntity]:
        subjects = self.subject_service.get_all_subjects()
        return subjects
