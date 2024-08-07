from ninja import Schema

from core.apps.schedule.entities.subject import Subject as SubjectEntity


class SubjectSchema(Schema):
    id: int
    title: str
    slug: str

    @classmethod
    def from_entity(cls, entity: SubjectEntity) -> 'SubjectSchema':
        return cls(
            id=entity.id,
            title=entity.title,
            slug=entity.slug,
        )


class SubjectInSchema(Schema):
    title: str




