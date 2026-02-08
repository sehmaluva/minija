"""API views for Organization management."""

import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.models.organization import (
    Organization,
    OrganizationMembership,
    OrganizationInvitation,
)
from apps.users.api.organization_serializers import (
    OrganizationSerializer,
    OrganizationCreateSerializer,
    OrganizationUpdateSerializer,
    MembershipSerializer,
    UpdateMemberRoleSerializer,
    InviteMemberSerializer,
    InvitationSerializer,
)
from apps.users.permissions import IsOrganizationOwner, IsOrganizationAdmin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Organization CRUD
# ---------------------------------------------------------------------------


class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/organizations/           – list user's organizations
    POST /api/organizations/           – create a new organization
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def get_queryset(self):
        return self.request.user.get_organizations()


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/organizations/<pk>/    – detail
    PATCH  /api/organizations/<pk>/    – update  (owner / admin only)
    DELETE /api/organizations/<pk>/    – soft-delete (owner only)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return OrganizationUpdateSerializer
        return OrganizationSerializer

    def get_queryset(self):
        return self.request.user.get_organizations()

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), IsOrganizationOwner()]
        if self.request.method in ("PUT", "PATCH"):
            return [permissions.IsAuthenticated(), IsOrganizationAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        logger.info("Organization '%s' soft-deleted", instance.name)


# ---------------------------------------------------------------------------
# Member management
# ---------------------------------------------------------------------------


class OrganizationMembersView(generics.ListAPIView):
    """
    GET /api/organizations/<pk>/members/
    """

    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_pk = self.kwargs["pk"]
        return OrganizationMembership.objects.filter(
            organization_id=org_pk,
            organization__memberships__user=self.request.user,
            organization__memberships__is_active=True,
            is_active=True,
        ).select_related("user")


class InviteMemberView(APIView):
    """
    POST /api/organizations/<pk>/members/invite/
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def post(self, request, pk):
        from apps.users.services.organization_service import invite_member

        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Permission check
        if not request.user.is_admin_of(organization):
            return Response(
                {"error": "You do not have permission to invite members."},
                status=status.HTTP_403_FORBIDDEN,
            )

        invitation, error = invite_member(
            organization,
            serializer.validated_data["email"],
            serializer.validated_data["role"],
            request.user,
        )

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            InvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED,
        )


class UpdateMemberRoleView(APIView):
    """
    PATCH /api/organizations/<pk>/members/<user_id>/role/
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationOwner]

    def patch(self, request, pk, user_id):
        serializer = UpdateMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            membership = OrganizationMembership.objects.get(
                organization_id=pk, user_id=user_id, is_active=True
            )
        except OrganizationMembership.DoesNotExist:
            return Response(
                {"error": "Membership not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if membership.role == "owner":
            return Response(
                {
                    "error": "Cannot change the owner's role. Transfer ownership instead."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.role = serializer.validated_data["role"]
        membership.save(update_fields=["role", "updated_at"])

        return Response(MembershipSerializer(membership).data)


class RemoveMemberView(APIView):
    """
    DELETE /api/organizations/<pk>/members/<user_id>/
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def delete(self, request, pk, user_id):
        from apps.users.services.organization_service import remove_member
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            organization = Organization.objects.get(pk=pk)
            user_to_remove = User.objects.get(pk=user_id)
        except (Organization.DoesNotExist, User.DoesNotExist):
            return Response(
                {"error": "Organization or user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        success, error = remove_member(organization, user_to_remove, request.user)
        if not success:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Member removed successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------------


class AcceptInvitationView(APIView):
    """
    POST /api/invitations/<token>/accept/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token):
        from apps.users.services.organization_service import accept_invitation

        membership, error = accept_invitation(token, request.user)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": f"You have joined {membership.organization.name}.",
                "membership": MembershipSerializer(membership).data,
            },
            status=status.HTTP_200_OK,
        )


class PendingInvitationsView(generics.ListAPIView):
    """
    GET /api/invitations/pending/
    """

    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrganizationInvitation.objects.filter(
            email=self.request.user.email, status="pending"
        ).select_related("organization", "invited_by")


class RevokeInvitationView(APIView):
    """
    DELETE /api/invitations/<pk>/
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def delete(self, request, pk):
        try:
            invitation = OrganizationInvitation.objects.get(pk=pk, status="pending")
        except OrganizationInvitation.DoesNotExist:
            return Response(
                {"error": "Invitation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check the requester is admin/owner of that org
        if not request.user.is_admin_of(invitation.organization):
            return Response(
                {"error": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        invitation.status = "revoked"
        invitation.save(update_fields=["status"])

        return Response(
            {"message": "Invitation revoked."},
            status=status.HTTP_200_OK,
        )
