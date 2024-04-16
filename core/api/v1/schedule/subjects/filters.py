from ninja import Schema


class SubjectFilter(Schema):
    search: str | None = None