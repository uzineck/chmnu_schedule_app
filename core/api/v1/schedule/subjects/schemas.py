from ninja import Schema

from core.apps.schedule.entities.subject import Subject as SubjectEntity


class SubjectSchema(Schema):
    id: int
    title: str
    slug: str

    @staticmethod
    def from_entity(entity: SubjectEntity) -> 'SubjectSchema':
        return SubjectSchema(
            id=entity.id,
            title=entity.title,
            slug=entity.slug,
        )


class SubjectCreateInSchema(Schema):
    title: str


class SubjectUpdateInSchema(Schema):
    subject_id: int
    title: str


class SubjectDeleteInSchema(Schema):
    subject_id: int




