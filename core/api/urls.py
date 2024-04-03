from django.http import HttpRequest, JsonResponse
from django.urls import path
from ninja import NinjaAPI

from core.api.schemas import PingResponseSchema

api = NinjaAPI()


@api.get('/ping', response=PingResponseSchema)
def ping(request: HttpRequest) -> PingResponseSchema:
    return PingResponseSchema(result=False)


urlpatterns = [
    path('', api.urls),
]
