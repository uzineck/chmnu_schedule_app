from ninja import Schema

from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity


class TeacherSchema(Schema):
    id: int
    last_name: str
    first_name: str
    middle_name: str
    rank: TeachersDegree

    @staticmethod
    def from_entity(entity: TeacherEntity) -> 'TeacherSchema':
        return TeacherSchema(
            id=entity.id,
            last_name=entity.last_name,
            first_name=entity.first_name,
            middle_name=entity.middle_name,
            rank=entity.rank,
        )


class TeacherInSchema(Schema):
    last_name: str
    first_name: str
    middle_name: str
    rank: TeachersDegree


class TeacherUpdateSubjectsInSchema(Schema):
    subject_id: int


