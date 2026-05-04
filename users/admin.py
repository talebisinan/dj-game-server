from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "nickname", "full_name", "is_active", "created_at")
    search_fields = ("email", "nickname", "full_name")
    list_filter = ("is_active", "nickname", "created_at")

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("nickname", {"fields": ("nickname",)}),
        ("Personal info", {"fields": ("full_name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        (
            "Personal info",
            {
                "classes": ("wide",),
                "fields": ("full_name", "nickname"),
            },
        ),
    )
