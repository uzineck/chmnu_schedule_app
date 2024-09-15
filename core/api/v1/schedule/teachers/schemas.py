from ninja import Schema

from core.apps.common.models import TeachersDegree
from core.apps.schedule.entities.teacher import Teacher as TeacherEntity


class TeacherSchema(Schema):
    uuid: str
    last_name: str
    first_name: str
    middle_name: str
    rank: TeachersDegree

    @classmethod
    def from_entity(cls, entity: TeacherEntity) -> 'TeacherSchema':
        return cls(
            uuid=entity.uuid,
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
    subject_uuid: str
