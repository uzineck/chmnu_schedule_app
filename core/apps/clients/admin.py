from django.contrib import admin

from core.apps.clients.models.client import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'middle_name', 'role', 'email', 'created_at', 'updated_at')
