from ninja import Schema


class SubjectCreateInSchema(Schema):
    title: str


class SubjectCreateOutSchema(Schema):
    title: str
    slug: str


class SubjectGetOutSchema(Schema):
    title: str
    slug: str


class SubjectUpdateInSchema(Schema):
    subject_id: int
    title: str


class SubjectUpdateOutSchema(Schema):
    title: str



