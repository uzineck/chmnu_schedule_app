import dataclasses
import logging
from typing import Any

from django.http import HttpRequest
from ninja import NinjaAPI

from core.apps.common.exceptions import ServiceException


logger = logging.getLogger(__name__)


def _exception_data(exc: ServiceException) -> dict[str, Any]:
    if not dataclasses.is_dataclass(exc):
        return {}
    return {
        field.name: getattr(exc, field.name)
        for field in dataclasses.fields(exc)
    }


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(ServiceException)
    def handle_service_exception(request: HttpRequest, exc: ServiceException):
        code = type(exc).get_code()
        data = _exception_data(exc)
        logger.log(
            exc.log_level,
            "%s code=%s status=%d path=%s data=%s",
            type(exc).__name__,
            code,
            exc.http_status,
            request.path,
            data,
        )
        return api.create_response(
            request,
            {
                "data": {},
                "meta": {},
                "errors": [
                    {
                        "code": code,
                        "message": exc.message,
                        "data": data,
                    },
                ],
            },
            status=exc.http_status,
        )
