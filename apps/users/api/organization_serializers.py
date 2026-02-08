"""Serializers for Organization management."""

from rest_framework import serializers
from apps.users.models.organization import (
    Organization,
    OrganizationMembership,
    OrganizationInvitation,
)
from apps.users.api.serializers import UserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    """Read serializer for organizations."""

    owner = UserSerializer(read_only=True)
    member_count = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "owner",
            "member_count",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "owner", "created_at", "updated_at")


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating organizations."""

    class Meta:
        model = Organization
        fields = ("name", "description")

    def create(self, validated_data):
        from apps.users.services.organization_service import create_organization

        user = self.context["request"].user
        return create_organization(
            user,
            validated_data["name"],
            validated_data.get("description", ""),
        )


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for updating organizations."""

    class Meta:
        model = Organization
        fields = ("name", "description")


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for organization memberships."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = (
            "id",
            "user",
            "role",
            "is_active",
            "joined_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "joined_at", "updated_at")


class UpdateMemberRoleSerializer(serializers.Serializer):
    """Serializer for updating a member's role."""

    role = serializers.ChoiceField(choices=["admin", "worker"])


class InviteMemberSerializer(serializers.Serializer):
    """Serializer for inviting a new member."""

    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["admin", "worker"], default="worker")


class InvitationSerializer(serializers.ModelSerializer):
    """Read serializer for invitations."""

    organization = OrganizationSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)

    class Meta:
        model = OrganizationInvitation
        fields = (
            "id",
            "organization",
            "email",
            "role",
            "invited_by",
            "token",
            "status",
            "expires_at",
            "created_at",
            "accepted_at",
        )
        read_only_fields = fields
