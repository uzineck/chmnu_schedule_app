import uuid
from calendar import timegm
from datetime import datetime


def get_new_uuid() -> str:
    return str(uuid.uuid4())


def convert_to_timestamp(datetime_obj: datetime) -> int:
    return timegm(datetime_obj.utctimetuple())
