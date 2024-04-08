from django.http import HttpRequest, JsonResponse
from django.urls import path
from ninja import NinjaAPI


api = NinjaAPI(
    title="CHMNU Schedule app",
    description="This is an api for CHMNU schedule",
)


@api.get("ping/")
def ping(request: HttpRequest):
    return {"status": "ok"}


urlpatterns = [
    path('', api.urls),
]
