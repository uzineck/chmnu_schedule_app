from dataclasses import dataclass
from pytils.translit import slugify

from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.services.subject import BaseSubjectService


@dataclass
class CreateSubjectUseCase:
    subject_service: BaseSubjectService

    def execute(self, title: str) -> SubjectEntity:
        slug = slugify(title)
        subject = self.subject_service.create(title=title, slug=slug)
        return subject
