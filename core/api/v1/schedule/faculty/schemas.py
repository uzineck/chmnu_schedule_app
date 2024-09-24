from ninja import Schema

from core.apps.schedule.entities.faculty import Faculty as FacultyEntity


class FacultySchema(Schema):
    uuid: str
    name: str
    code_name: str

    @classmethod
    def from_entity(cls, entity: FacultyEntity) -> 'FacultySchema':
        return cls(
            uuid=entity.uuid,
            name=entity.name,
            code_name=entity.code_name,
        )


class FacultyCodeNameSchema(Schema):
    code_name: str

    @classmethod
    def from_entity(cls, entity: FacultyEntity) -> 'FacultyCodeNameSchema':
        return cls(
            code_name=entity.code_name,
        )


class FacultyInSchema(Schema):
    name: str
    code_name: str
