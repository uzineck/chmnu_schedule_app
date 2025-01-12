import factory
from factory.django import DjangoModelFactory

from core.apps.clients.models import Role
from core.apps.common.models import ClientRole


class RoleModelFactory(DjangoModelFactory):
    id = factory.Iterator(ClientRole.values)

    class Meta:
        model = Role
