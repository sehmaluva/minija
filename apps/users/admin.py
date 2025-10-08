from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_staff", "created_at")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number", "role")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {"fields": ("email", "phone_number", "role", "first_name", "last_name")},
        ),
    )
