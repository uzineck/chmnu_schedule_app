from django.urls import path
from ninja import NinjaAPI

from core.api.v1.urls import router as v1_router


api = NinjaAPI(
    title="CHMNU Schedule app",
    description="This is an api for CHMNU schedule",
    csrf=True,
)


api.add_router('v1/', v1_router)

urlpatterns = [
    path('', api.urls),
]
