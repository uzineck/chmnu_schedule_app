from abc import ABC, abstractmethod

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter
from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.subject import Subject as SubjectEntity
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity
from core.apps.schedule.models.teachers import Teacher as TeacherModel


class BaseTeacherService(ABC):
    @abstractmethod
    def get_teacher_by_id(self, teacher_id: int):
        ...

    @abstractmethod
    def get_teacher_list(self, filters: SearchFilter, pagination: PaginationIn):
        ...

    @abstractmethod
    def get_or_create(self,
                      first_name: str,
                      last_name: str,
                      middle_name: str,
                      rank: TeachersDegree, ):
        ...

    @abstractmethod
    def update_teacher_by_id(self,
                             teacher_id: int,
                             first_name: str,
                             last_name: str,
                             middle_name: str,
                             rank: TeachersDegree):
        ...

    @abstractmethod
    def update_teacher_subjects(self, teacher_id: int, subjects: list[SubjectEntity]):
        ...


class ORMTeacherService(BaseTeacherService):
    def get_or_create(self,
                      first_name: str,
                      last_name: str,
                      middle_name: str,
                      rank: str, ):
        teacher, _ = TeacherModel.objects.get_or_create(first_name=first_name,
                                                        last_name=last_name,
                                                        middle_name=middle_name,
                                                        rank=rank)

        return teacher.to_entity()
