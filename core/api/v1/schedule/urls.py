from ninja import Router

from core.api.v1.schedule.groups.handlers import router as group_router
from core.api.v1.schedule.lessons.handlers import router as lesson_router
from core.api.v1.schedule.rooms.handlers import router as room_router
from core.api.v1.schedule.subjects.handlers import router as subject_router
from core.api.v1.schedule.teachers.handlers import router as teacher_router
from core.api.v1.schedule.timeslots.handlers import router as timeslot_router


router = Router(tags=['Schedule'])

router.add_router(prefix="group/", router=group_router)
router.add_router(prefix="lesson/", router=lesson_router)
router.add_router(prefix="teacher/", router=teacher_router)
router.add_router(prefix="subject/", router=subject_router)
router.add_router(prefix="room/", router=room_router)
router.add_router(prefix="timeslot/", router=timeslot_router)


