from django.urls import path
from ninja import NinjaAPI
from ninja.throttling import (
    AnonRateThrottle,
    AuthRateThrottle,
)

from core.api.exception_handlers import register_exception_handlers
from core.api.v1.urls import router as v1_router


api = NinjaAPI(
    title="CHMNU Schedule app",
    description="This is an api for CHMNU schedule",
    throttle=[
        AnonRateThrottle('10/s'),
        AuthRateThrottle('50/s'),
    ],
)

register_exception_handlers(api)

api.add_router('v1/', v1_router)

urlpatterns = [
    path('', api.urls),
]
