from django.http import HttpRequest
from ninja import Router

from core.api.v1.clients.urls import router as client_router
from core.api.v1.schedule.urls import router as schedule_router
from core.api.v1.time.urls import router as time_router


router = Router(tags=['v1'])
router.add_router('time/', time_router)
router.add_router('clients/', client_router)
router.add_router('schedule/', schedule_router)


@router.get(
    "ping/",
    operation_id="ping",
    summary="Liveness probe",
    description="Returns `{\"status\": \"ok\"}` if the API process is up. Used by container healthchecks.",
)
def ping(request: HttpRequest):
    return {"status": "ok"}
