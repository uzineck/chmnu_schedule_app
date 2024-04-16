from ninja import Router

from core.api.v1.clients.sophomores.handlers import router as sophomore_router

router = Router(tags=['Clients'])

router.add_router(prefix="sophomore/", router=sophomore_router)


