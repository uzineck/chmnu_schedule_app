from ninja import Schema


class TeacherFilter(Schema):
    name: str | None = None
    rank: str | None = None

