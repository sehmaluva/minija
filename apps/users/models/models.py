"""Models for user management."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with OTP email verification and organization support.
    """

    ROLE_CHOICES = [
        ("admin", "System Administrator"),
        ("user", "System User"),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)

    # Email verification – link token
    email_verification_token = models.UUIDField(editable=True, unique=True, null=True)

    # Email verification – 6-digit OTP
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expires_at = models.DateTimeField(blank=True, null=True)
    verification_attempts = models.PositiveSmallIntegerField(default=0)
    last_otp_sent_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        """Class meta for User Model"""

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        """Returns the fullname of the user"""
        return f"{self.first_name} {self.last_name}".strip()

    # ------------------------------------------------------------------
    # Organization helpers
    # ------------------------------------------------------------------

    def get_organizations(self):
        """Return all active organizations this user belongs to."""
        from apps.users.models.organization import Organization

        return Organization.objects.filter(
            memberships__user=self,
            memberships__is_active=True,
        )

    def get_role_in_organization(self, organization):
        """Return the user's role in *organization*, or ``None``."""
        from apps.users.models.organization import OrganizationMembership

        try:
            membership = OrganizationMembership.objects.get(
                organization=organization, user=self, is_active=True
            )
            return membership.role
        except OrganizationMembership.DoesNotExist:
            return None

    def is_owner_of(self, organization):
        return self.get_role_in_organization(organization) == "owner"

    def is_admin_of(self, organization):
        return self.get_role_in_organization(organization) in ("owner", "admin")

    def is_member_of(self, organization):
        return self.get_role_in_organization(organization) is not None
