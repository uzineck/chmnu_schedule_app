from ninja import Router

from core.api.v1.time.handlers import router as time_router


router = Router(tags=['Time'])

router.add_router(prefix="time/", router=time_router)
