from ninja import Schema


class TeacherFilter(Schema):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    rank: str | None = None
