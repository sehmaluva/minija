from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models.models import User
from apps.users.models.organization import (
    Organization,
    OrganizationMembership,
    OrganizationInvitation,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_email_verified",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_email_verified", "is_staff", "created_at")
    search_fields = ("email", "username", "first_name", "last_name")
    readonly_fields = (
        "email_verification_token",
        "email_verification_code",
        "verification_code_expires_at",
        "verification_attempts",
        "last_otp_sent_at",
    )
    ordering = ("-created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number", "role")}),
        (
            "Email Verification",
            {
                "fields": (
                    "is_email_verified",
                    "email_verification_token",
                    "email_verification_code",
                    "verification_code_expires_at",
                    "verification_attempts",
                    "last_otp_sent_at",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {"fields": ("email", "phone_number", "role", "first_name", "last_name")},
        ),
    )


class MembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    readonly_fields = ("joined_at",)


class InvitationInline(admin.TabularInline):
    model = OrganizationInvitation
    extra = 0
    readonly_fields = ("token", "created_at")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug", "owner__email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [MembershipInline, InvitationInline]


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active")
    search_fields = ("organization__name", "user__email")


@admin.register(OrganizationInvitation)
class OrganizationInvitationAdmin(admin.ModelAdmin):
    list_display = ("organization", "email", "role", "status", "expires_at")
    list_filter = ("status", "role")
    search_fields = ("organization__name", "email")
    readonly_fields = ("token",)
