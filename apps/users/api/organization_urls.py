"""URL patterns for Organization management API."""

from django.urls import path

from apps.users.api.organization_views import (
    OrganizationListCreateView,
    OrganizationDetailView,
    OrganizationMembersView,
    InviteMemberView,
    UpdateMemberRoleView,
    RemoveMemberView,
    AcceptInvitationView,
    PendingInvitationsView,
    RevokeInvitationView,
)

urlpatterns = [
    # Organization CRUD
    path(
        "",
        OrganizationListCreateView.as_view(),
        name="organization_list_create",
    ),
    path(
        "<int:pk>/",
        OrganizationDetailView.as_view(),
        name="organization_detail",
    ),
    # Members
    path(
        "<int:pk>/members/",
        OrganizationMembersView.as_view(),
        name="organization_members",
    ),
    path(
        "<int:pk>/members/invite/",
        InviteMemberView.as_view(),
        name="organization_invite_member",
    ),
    path(
        "<int:pk>/members/<int:user_id>/role/",
        UpdateMemberRoleView.as_view(),
        name="organization_update_role",
    ),
    path(
        "<int:pk>/members/<int:user_id>/",
        RemoveMemberView.as_view(),
        name="organization_remove_member",
    ),
    # Invitations
    path(
        "invitations/<uuid:token>/accept/",
        AcceptInvitationView.as_view(),
        name="invitation_accept",
    ),
    path(
        "invitations/pending/",
        PendingInvitationsView.as_view(),
        name="invitations_pending",
    ),
    path(
        "invitations/<int:pk>/",
        RevokeInvitationView.as_view(),
        name="invitation_revoke",
    ),
]
