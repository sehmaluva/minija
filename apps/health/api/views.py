from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from apps.birds.models.models import Batch
from apps.health.models.models import HealthRecord, MortalityRecord
from .serializers import (
    HealthRecordSerializer,
    HealthRecordCreateSerializer,
    MortalityRecordSerializer,
)
from apps.users.permissions import IsOrganizationMember


def _get_org(request):
    return getattr(request, "organization", None)


class HealthRecordListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating health records."""

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["record_type", "batch", "date"]
    search_fields = ["description", "batch__batch_number"]
    ordering_fields = ["date", "created_at"]
    ordering = ["-date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return HealthRecordCreateSerializer
        return HealthRecordSerializer

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return HealthRecord.objects.none()
        return HealthRecord.objects.filter(organization=org)


class HealthRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting a health record."""

    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return HealthRecord.objects.none()
        return HealthRecord.objects.filter(organization=org)


class MortalityRecordListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating mortality records."""

    serializer_class = MortalityRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["cause_category", "batch", "date"]
    search_fields = ["specific_cause", "batch__batch_number"]
    ordering_fields = ["date", "count", "created_at"]
    ordering = ["-date"]

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return MortalityRecord.objects.none()
        return MortalityRecord.objects.filter(organization=org)


class MortalityRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting a mortality record."""

    serializer_class = MortalityRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return MortalityRecord.objects.none()
        return MortalityRecord.objects.filter(organization=org)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def health_dashboard_view(request):
    """API view for health dashboard statistics."""
    org = _get_org(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    batches = Batch.objects.filter(organization=org, status="active")

    # Recent health records
    recent_records = HealthRecord.objects.filter(
        organization=org, batch__in=batches
    ).order_by("-date")[:10]

    # Upcoming vaccinations
    upcoming_vaccinations = HealthRecord.objects.filter(
        organization=org,
        batch__in=batches,
        record_type="vaccination",
        vaccination_details__next_vaccination_date__gte=timezone.now().date(),
        vaccination_details__next_vaccination_date__lte=timezone.now().date()
        + timedelta(days=30),
    ).order_by("vaccination_details__next_vaccination_date")

    # Mortality statistics (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_mortality = MortalityRecord.objects.filter(
        organization=org, batch__in=batches, date__gte=thirty_days_ago
    )

    mortality_by_cause = list(
        recent_mortality.values("cause_category")
        .annotate(total_count=Sum("count"))
        .order_by("-total_count")
    )

    # Health alerts
    alerts = []
    for batch in batches:
        batch_mortality = (
            recent_mortality.filter(batch=batch).aggregate(total=Sum("count"))["total"]
            or 0
        )
        if batch_mortality > 0 and batch.current_count > 0:
            mortality_rate = (batch_mortality / batch.current_count) * 100
            if mortality_rate > 5:
                alerts.append(
                    {
                        "type": "high_mortality",
                        "batch_id": batch.batch_number,
                        "message": f"High mortality rate: {mortality_rate:.1f}% in last 30 days",
                        "severity": "high" if mortality_rate > 10 else "medium",
                    }
                )

    dashboard_data = {
        "recent_health_records": HealthRecordSerializer(recent_records, many=True).data,
        "upcoming_vaccinations": HealthRecordSerializer(
            upcoming_vaccinations, many=True
        ).data,
        "mortality_statistics": {
            "total_deaths_30_days": recent_mortality.aggregate(total=Sum("count"))[
                "total"
            ]
            or 0,
            "by_cause": mortality_by_cause,
            "average_age_at_death": recent_mortality.aggregate(avg=Avg("age_at_death"))[
                "avg"
            ]
            or 0,
        },
        "health_alerts": alerts,
        "summary": {
            "total_active_batches": batches.count(),
            "total_health_records": HealthRecord.objects.filter(
                organization=org, batch__in=batches
            ).count(),
            "vaccinations_this_month": HealthRecord.objects.filter(
                organization=org,
                batch__in=batches,
                record_type="vaccination",
                date__gte=timezone.now().date().replace(day=1),
            ).count(),
        },
    }

    return Response(dashboard_data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def flock_health_history_view(request, flock_id):
    """API view for getting complete health history of a batch."""
    org = _get_org(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        batch = Batch.objects.get(id=flock_id, organization=org)

        health_records = batch.health_records.all().order_by("-date")
        mortality_records = batch.mortality_records.all().order_by("-date")

        total_vaccinations = health_records.filter(record_type="vaccination").count()
        total_treatments = health_records.filter(record_type="treatment").count()
        total_deaths = mortality_records.aggregate(total=Sum("count"))["total"] or 0

        health_history = {
            "batch": {
                "id": batch.id,
                "batch_id": batch.batch_number,
                "current_count": batch.current_count,
                "age_in_days": batch.age_in_days,
            },
            "health_records": HealthRecordSerializer(health_records, many=True).data,
            "mortality_records": MortalityRecordSerializer(
                mortality_records, many=True
            ).data,
            "health_metrics": {
                "total_vaccinations": total_vaccinations,
                "total_treatments": total_treatments,
                "total_deaths": total_deaths,
                "mortality_rate": (
                    (total_deaths / batch.initial_count * 100)
                    if batch.initial_count > 0
                    else 0
                ),
                "health_cost": health_records.aggregate(total=Sum("cost"))["total"]
                or 0,
            },
        }

        return Response(health_history)

    except Batch.DoesNotExist:
        return Response({"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)
