from ninja import Schema

from core.apps.schedule.entities.subject import Subject as SubjectEntity


class SubjectSchema(Schema):
    uuid: str
    title: str
    slug: str

    @classmethod
    def from_entity(cls, entity: SubjectEntity) -> 'SubjectSchema':
        return cls(
            uuid=entity.uuid,
            title=entity.title,
            slug=entity.slug,
        )


class SubjectInSchema(Schema):
    title: str


class UpdateSubjectTitleSchema(Schema):
    subject_uuid: str
    new_title: str
