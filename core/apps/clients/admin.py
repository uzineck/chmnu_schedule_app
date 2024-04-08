from django.contrib import admin

from core.apps.clients.models.sophomors import Sophomore


@admin.register(Sophomore)
class SophomoreAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'token', 'created_at', 'updated_at',)