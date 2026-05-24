from django.urls import path
from ninja import NinjaAPI
from ninja.throttling import (
    AnonRateThrottle,
    AuthRateThrottle,
)

from core.api.exception_handlers import register_exception_handlers
from core.api.v1.urls import router as v1_router


api = NinjaAPI(
    title="CHMNU Schedule app",
    version="1.0.0",
    description=(
        "REST API for CHMNU university schedule management.\n\n"
        "## Authentication\n"
        "Most write endpoints and all admin endpoints require a Bearer access token in the "
        "`Authorization` header. The access token is obtained from `POST /clients/client/log-in` "
        "and refreshed via `POST /clients/client/update_access_token`, which reads the "
        "`refresh_token` cookie (HttpOnly, SameSite=Strict) and never echoes the refresh token in "
        "the response body.\n\n"
        "## Roles\n"
        "Authorization is role-based. A single client may hold any combination of: ADMIN, "
        "HEADMAN, CLIENT_MANAGER, FACULTY_MANAGER, TEACHER_MANAGER, SUBJECT_MANAGER, "
        "ROOM_MANAGER, GROUP_MANAGER, SCHEDULE_MANAGER. ADMIN implicitly satisfies every "
        "manager role.\n\n"
        "## Response envelope\n"
        "Successful responses are wrapped as `{ \"data\": ..., \"meta\": {}, \"errors\": [] }`. "
        "Error responses use the same envelope with `data = {}` and a populated `errors` list — "
        "each entry exposes a stable `code` (e.g. `FACULTY_NOT_FOUND`) plus an English-only "
        "`message` and a per-exception `data` payload. Clients should localize on `code`.\n\n"
        "## Rate limits\n"
        "Anonymous: 10 req/s. Authenticated: 50 req/s."
    ),
    throttle=[
        AnonRateThrottle('10/s'),
        AuthRateThrottle('50/s'),
    ],
)

register_exception_handlers(api)

api.add_router('v1/', v1_router)

urlpatterns = [
    path('', api.urls),
]
