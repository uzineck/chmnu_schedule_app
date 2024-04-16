from ninja import Router

from core.api.v1.schedule.subjects.handlers import router as subject_router

router = Router(tags=['Schedule'])

router.add_router(prefix="subject/", router=subject_router)


