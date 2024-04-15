from ninja import Router

from core.api.v1.schedule.sophomores.handlers import router as sophomore_router

router = Router(tags=['Schedule'])

router.add_router(prefix="sophomore/", router=sophomore_router)


