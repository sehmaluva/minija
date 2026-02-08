from rest_framework import viewsets, permissions
from apps.orders.models import ChickOrder, Reminder
from .serializers import ChickOrderSerializer, ReminderSerializer
from apps.users.permissions import IsOrganizationMember


class OrganizationScopedViewSet(viewsets.ModelViewSet):
    """Base viewset that scopes querysets to the active organization."""

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        if not org:
            return self.model.objects.none()
        return self.model.objects.filter(organization=org).order_by("-date")

    def perform_create(self, serializer):
        org = getattr(self.request, "organization", None)
        serializer.save(organization=org)


class ChickOrderViewSet(OrganizationScopedViewSet):
    serializer_class = ChickOrderSerializer
    model = ChickOrder


class ReminderViewSet(OrganizationScopedViewSet):
    serializer_class = ReminderSerializer
    model = Reminder
