from django.db import models

from core.apps.common.models import ClientRole


class Role(models.Model):
    id = models.CharField(choices=ClientRole, primary_key=True)

    def __str__(self):
        return self.get_id_display()
