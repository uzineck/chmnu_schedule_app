from core.apps.common.authentication.bearer import JWTBearer
from core.apps.common.models import ClientRole


jwt_auth_admin = JWTBearer([ClientRole.ADMIN])
jwt_auth_headman = JWTBearer([ClientRole.HEADMAN])

jwt_auth_client_manager = JWTBearer([ClientRole.CLIENT_MANAGER, ClientRole.ADMIN])
jwt_auth_faculty_manager = JWTBearer([ClientRole.FACULTY_MANAGER, ClientRole.ADMIN])
jwt_auth_room_manager = JWTBearer([ClientRole.ROOM_MANAGER, ClientRole.ADMIN])
jwt_auth_subject_manager = JWTBearer([ClientRole.SUBJECT_MANAGER, ClientRole.ADMIN])
jwt_auth_group_manager = JWTBearer([ClientRole.GROUP_MANAGER, ClientRole.ADMIN])
jwt_auth_schedule_manager = JWTBearer([ClientRole.SCHEDULE_MANAGER, ClientRole.ADMIN])
jwt_auth_teacher_manager = JWTBearer([ClientRole.TEACHER_MANAGER, ClientRole.ADMIN])

jwt_auth = JWTBearer([
    ClientRole.ADMIN,
    ClientRole.HEADMAN,
    ClientRole.FACULTY_MANAGER,
    ClientRole.CLIENT_MANAGER,
    ClientRole.TEACHER_MANAGER,
    ClientRole.GROUP_MANAGER,
    ClientRole.SUBJECT_MANAGER,
    ClientRole.ROOM_MANAGER,
    ClientRole.SCHEDULE_MANAGER,
])
