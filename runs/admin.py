from django.contrib import admin

from runs.models import Run


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "invite_code", "is_started", "created_at")
