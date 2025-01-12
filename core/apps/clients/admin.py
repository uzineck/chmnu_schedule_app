from django.contrib import admin

from core.apps.clients.models import IssuedJwtToken
from core.apps.clients.models.client import Client
from core.apps.clients.models.role import Role


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'middle_name', 'email', 'created_at', 'updated_at']
    list_display_links = ['id', 'last_name', 'first_name', 'middle_name', 'email']
    list_filter = ['roles', 'created_at', 'updated_at']
    search_fields = ['id', 'last_name', 'first_name', 'middle_name', 'email']


@admin.register(IssuedJwtToken)
class IssuedJwtTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'jti', 'device_id', 'expiration_time', 'revoked']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id']
