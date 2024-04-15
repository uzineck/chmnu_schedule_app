from pydantic import BaseModel, Field

from typing import Any, Generic, TypeVar

from ninja import Schema


TData = TypeVar("TData")


class ApiResponse(Schema, Generic[TData]):
    data: TData | dict = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[Any] = Field(default_factory=list)
