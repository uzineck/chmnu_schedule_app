from ninja import Router

from core.api.v1.schedule.urls import router as schedule_router

router = Router(tags=['v1'])
router.add_router('schedule/', schedule_router)

