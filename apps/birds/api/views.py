"""Batch API views for listing, creating, updating, and retrieving batch statistics and performance."""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Avg
from apps.birds.models.models import Batch
from apps.birds.api.serializers import BatchSerializer
from apps.users.permissions import IsOrganizationMember, IsOrganizationAdmin


def _get_org_or_error(request):
    """Return the organization from request or None."""
    return getattr(request, "organization", None)


class BatchListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating batches."""

    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["batch_number"]
    ordering_fields = ["batch_id", "current_count", "collection_date", "created_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        org = _get_org_or_error(self.request)
        if not org:
            return Batch.objects.none()
        return Batch.objects.filter(organization=org)


class BatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting a batch."""

    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        org = _get_org_or_error(self.request)
        if not org:
            return Batch.objects.none()
        return Batch.objects.filter(organization=org)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated(), IsOrganizationAdmin()]
        return [permissions.IsAuthenticated(), IsOrganizationMember()]


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def batch_statistics_view(request):
    """API view for getting batch statistics."""
    org = _get_org_or_error(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    batches = Batch.objects.filter(organization=org)
    active_batches = batches.filter(status="active")

    stats = {
        "total_flocks": batches.count(),
        "active_batches": active_batches.count(),
        "total_birds": active_batches.aggregate(total=Sum("current_count"))["total"]
        or 0,
        "average_batch_size": active_batches.aggregate(avg=Avg("current_count"))["avg"]
        or 0,
        "mortality_stats": {},
    }

    inactive_batches = batches.exclude(status="active")
    for batch_status, _ in Batch.STATUS_CHOICES:
        if batch_status != "active":
            count = inactive_batches.filter(status=batch_status).count()
            if count > 0:
                stats["mortality_stats"][batch_status] = count

    return Response(stats)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def batch_performance_view(request, batch_id):
    """API view for getting detailed batch performance metrics."""
    org = _get_org_or_error(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        batch = Batch.objects.get(id=batch_id, organization=org)

        age_weeks = batch.age_in_days / 7
        survival_rate = (
            (batch.current_count / batch.initial_count * 100)
            if batch.initial_count > 0
            else 0
        )

        weight_data = []

        performance_data = {
            "batch": BatchSerializer(batch).data,
            "metrics": {
                "age_weeks": round(age_weeks, 1),
                "survival_rate": round(survival_rate, 2),
                "mortality_rate": round(100 - survival_rate, 2),
                "birds_lost": batch.initial_count - batch.current_count,
            },
            "weight_data": weight_data,
        }

        return Response(performance_data)

    except Batch.DoesNotExist:
        return Response({"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def bulk_batch_update_view(request):
    """API view for bulk updating batch counts (for mortality, sales, etc.)."""
    org = _get_org_or_error(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    batch_updates = request.data.get("batch_updates", [])
    if not batch_updates:
        return Response(
            {"error": "No batch updates provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    updated_batches = []
    errors = []

    for update in batch_updates:
        try:
            bid = update.get("batch_id")
            new_count = update.get("new_count")

            batch = Batch.objects.get(id=bid, organization=org)
            batch.current_count = new_count
            if new_count <= 0:
                batch.status = "deceased"
            batch.save()

            updated_batches.append(BatchSerializer(batch).data)

        except Batch.DoesNotExist:
            errors.append(f"Batch with id {bid} not found")
        except Exception as e:
            errors.append(f"Error updating batch {bid}: {str(e)}")

    return Response({"updated_batches": updated_batches, "errors": errors})
