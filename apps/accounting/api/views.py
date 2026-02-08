from rest_framework import viewsets, permissions
from apps.accounting.models.models import Sale, Cost, Transaction
from .serializers import SaleSerializer, CostSerializer, TransactionSerializer
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


class SaleViewSet(OrganizationScopedViewSet):
    serializer_class = SaleSerializer
    model = Sale


class CostViewSet(OrganizationScopedViewSet):
    serializer_class = CostSerializer
    model = Cost


class TransactionViewSet(OrganizationScopedViewSet):
    serializer_class = TransactionSerializer
    model = Transaction
