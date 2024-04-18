from ninja import Router

from core.api.v1.schedule.subjects.handlers import router as subject_router
from core.api.v1.schedule.rooms.handlers import router as room_router
from core.api.v1.schedule.timeslots.handlers import router as timeslot_router

router = Router(tags=['Schedule'])

router.add_router(prefix="subject/", router=subject_router)
router.add_router(prefix="room/", router=room_router)
router.add_router(prefix="timeslot/", router=timeslot_router)


