import uuid


def get_new_uuid() -> str:
    return str(uuid.uuid4())
