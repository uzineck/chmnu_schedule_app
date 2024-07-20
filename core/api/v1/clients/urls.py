from ninja import Router

from core.api.v1.clients.admin.handlers import router as admin_router
from core.api.v1.clients.client.handlers import router as client_router


router = Router(tags=['Clients'])

router.add_router(prefix="client/", router=client_router)
router.add_router(prefix="admin/", router=admin_router)
