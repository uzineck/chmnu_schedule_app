from ninja import Schema

from pydantic import Field
from typing import (
    Any,
    Generic,
    TypeVar,
)

from core.api.filters import PaginationOut


TData = TypeVar("TData")
TListItem = TypeVar("TListItem")


class StatusResponse(Schema):
    status: str


class ListPaginatedResponse(Schema, Generic[TListItem]):
    items: list[TListItem]
    pagination: PaginationOut


class ApiErrorDetail(Schema):
    code: str = Field(
        description="Machine-readable error code derived from the exception class name "
        "(SCREAMING_SNAKE).",
    )
    message: str = Field(description="Human-readable error message in English; clients should localize via `code`.")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-exception payload (dataclass fields of the raised ServiceException).",
    )


class ApiResponse(Schema, Generic[TData]):
    """Success envelope (2xx).

    `errors` is empty on a fully-successful response but may carry one or more
    `ApiErrorDetail` entries to communicate non-fatal warnings or soft conflicts
    alongside the returned `data` (e.g. partial-success in bulk operations).
    Hard failures use `ApiErrorResponse` instead.

    """
    data: TData
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[ApiErrorDetail] = Field(default_factory=list)


class ApiErrorResponse(Schema):
    """Error envelope (4xx/5xx) emitted by the global `ServiceException`
    handler.

    `data` is always an empty object; `errors` lists at least one
    `ApiErrorDetail` describing what went wrong.

    """
    data: dict = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[ApiErrorDetail]
