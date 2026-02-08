from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Avg, F, Count
from django.utils import timezone
from datetime import timedelta, datetime
from apps.birds.models.models import Batch
from apps.reports.models.models import Report, Alert
from apps.reports.api.serializers import (
    ReportSerializer,
    ReportCreateSerializer,
    AlertSerializer,
    AlertUpdateSerializer,
)
from apps.users.permissions import IsOrganizationMember


def _get_org(request):
    return getattr(request, "organization", None)


class ReportListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating reports."""

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["report_type", "report_format"]
    search_fields = ["title"]
    ordering_fields = ["generated_at", "title"]
    ordering = ["-generated_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReportCreateSerializer
        return ReportSerializer

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return Report.objects.none()
        return Report.objects.filter(organization=org)


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting a report."""

    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return Report.objects.none()
        return Report.objects.filter(organization=org)


class AlertListView(generics.ListAPIView):
    """API view for listing alerts."""

    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["alert_type", "severity", "is_read", "is_resolved"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "severity"]
    ordering = ["-created_at"]

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return Alert.objects.none()
        return Alert.objects.filter(organization=org)


class AlertDetailView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating an alert."""

    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AlertUpdateSerializer
        return AlertSerializer

    def get_queryset(self):
        org = _get_org(self.request)
        if not org:
            return Alert.objects.none()
        return Alert.objects.filter(organization=org)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_dashboard_view(request):
    """API view for comprehensive analytics dashboard."""
    org = _get_org(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    batches = Batch.objects.filter(organization=org, status="active")

    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    # Batch statistics
    total_birds = batches.aggregate(total=Sum("current_count"))["total"] or 0
    batch_stats = {
        "total_flocks": batches.count(),
        "total_birds": total_birds,
        "average_batch_size": batches.aggregate(avg=Avg("current_count"))["avg"] or 0,
    }

    # Production analytics
    from apps.production.models.models import EggProduction, FeedRecord

    recent_egg_production = EggProduction.objects.filter(
        organization=org, batch__in=batches, date__gte=last_30_days
    )

    egg_analytics = {
        "total_eggs_30_days": recent_egg_production.aggregate(total=Sum("total_eggs"))[
            "total"
        ]
        or 0,
        "average_production_rate": recent_egg_production.aggregate(
            avg=Avg("production_rate")
        )["avg"]
        or 0,
        "grade_distribution": {
            "grade_a": recent_egg_production.aggregate(total=Sum("grade_a_eggs"))[
                "total"
            ]
            or 0,
            "grade_b": recent_egg_production.aggregate(total=Sum("grade_b_eggs"))[
                "total"
            ]
            or 0,
            "grade_c": recent_egg_production.aggregate(total=Sum("grade_c_eggs"))[
                "total"
            ]
            or 0,
            "cracked": recent_egg_production.aggregate(total=Sum("cracked_eggs"))[
                "total"
            ]
            or 0,
            "dirty": recent_egg_production.aggregate(total=Sum("dirty_eggs"))["total"]
            or 0,
        },
    }

    recent_feed = FeedRecord.objects.filter(
        organization=org, batch__in=batches, date__gte=last_30_days
    )

    feed_analytics = {
        "total_consumption_30_days": recent_feed.aggregate(total=Sum("quantity_kg"))[
            "total"
        ]
        or 0,
        "total_cost_30_days": sum(
            record.quantity_kg * record.cost_per_kg for record in recent_feed
        ),
        "feed_by_type": list(
            recent_feed.values("feed_type")
            .annotate(total_kg=Sum("quantity_kg"), avg_cost=Avg("cost_per_kg"))
            .order_by("-total_kg")
        ),
        "top_suppliers": list(
            recent_feed.values("supplier")
            .annotate(total_kg=Sum("quantity_kg"))
            .order_by("-total_kg")[:5]
        ),
    }

    # Health analytics
    from apps.health.models.models import HealthRecord, MortalityRecord

    recent_health = HealthRecord.objects.filter(
        organization=org, batch__in=batches, date__gte=last_30_days
    )
    recent_mortality = MortalityRecord.objects.filter(
        organization=org, batch__in=batches, date__gte=last_30_days
    )

    health_analytics = {
        "total_health_records_30_days": recent_health.count(),
        "vaccinations_30_days": recent_health.filter(record_type="vaccination").count(),
        "treatments_30_days": recent_health.filter(record_type="treatment").count(),
        "total_mortality_30_days": recent_mortality.aggregate(total=Sum("count"))[
            "total"
        ]
        or 0,
        "mortality_by_cause": list(
            recent_mortality.values("cause_category")
            .annotate(total=Sum("count"))
            .order_by("-total")
        ),
        "health_cost_30_days": recent_health.aggregate(total=Sum("cost"))["total"] or 0,
    }

    # Financial analytics
    financial_analytics = {
        "feed_costs_30_days": feed_analytics["total_cost_30_days"],
        "health_costs_30_days": health_analytics["health_cost_30_days"],
        "total_operational_costs_30_days": feed_analytics["total_cost_30_days"]
        + health_analytics["health_cost_30_days"],
        "cost_per_bird_30_days": (
            (
                feed_analytics["total_cost_30_days"]
                + health_analytics["health_cost_30_days"]
            )
            / total_birds
            if total_birds > 0
            else 0
        ),
    }

    # Performance indicators
    performance_indicators = {
        "overall_survival_rate": (
            sum(
                (
                    (b.current_count / b.initial_count * 100)
                    if b.initial_count > 0
                    else 0
                )
                for b in batches
            )
            / batches.count()
            if batches.count() > 0
            else 0
        ),
    }

    # Recent alerts
    recent_alerts = Alert.objects.filter(
        organization=org,
        created_at__gte=timezone.now() - timedelta(days=7),
        is_resolved=False,
    ).order_by("-created_at")[:10]

    dashboard_data = {
        "batch_statistics": batch_stats,
        "production_analytics": {
            "egg_production": egg_analytics,
            "feed_consumption": feed_analytics,
        },
        "health_analytics": health_analytics,
        "financial_analytics": financial_analytics,
        "performance_indicators": performance_indicators,
        "recent_alerts": AlertSerializer(recent_alerts, many=True).data,
        "summary": {
            "total_flocks": batch_stats["total_flocks"],
            "total_birds": total_birds,
            "unresolved_alerts": recent_alerts.count(),
        },
    }

    return Response(dashboard_data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def generate_report_view(request):
    """API view for generating custom reports."""
    org = _get_org(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    report_type = request.data.get("report_type")
    start_date = request.data.get("start_date")
    end_date = request.data.get("end_date")
    batch_ids = request.data.get("batch_ids", [])

    if not all([report_type, start_date, end_date]):
        return Response(
            {"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = request.user
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if batch_ids:
            batches = Batch.objects.filter(id__in=batch_ids, organization=org)
        else:
            batches = Batch.objects.filter(organization=org)

        report_data = {}

        if report_type == "production":
            from apps.production.models.models import EggProduction, FeedRecord

            egg_production = EggProduction.objects.filter(
                organization=org, batch__in=batches, date__range=[start_date, end_date]
            )
            feed_records = FeedRecord.objects.filter(
                organization=org, batch__in=batches, date__range=[start_date, end_date]
            )

            report_data = {
                "total_eggs": egg_production.aggregate(total=Sum("total_eggs"))["total"]
                or 0,
                "average_production_rate": egg_production.aggregate(
                    avg=Avg("production_rate")
                )["avg"]
                or 0,
                "total_feed_consumed": feed_records.aggregate(total=Sum("quantity_kg"))[
                    "total"
                ]
                or 0,
                "total_feed_cost": sum(
                    r.quantity_kg * r.cost_per_kg for r in feed_records
                ),
                "batches_included": batches.count(),
                "date_range": f"{start_date} to {end_date}",
            }

        elif report_type == "health":
            from apps.health.models.models import HealthRecord, MortalityRecord

            health_records = HealthRecord.objects.filter(
                organization=org, batch__in=batches, date__range=[start_date, end_date]
            )
            mortality_records = MortalityRecord.objects.filter(
                organization=org, batch__in=batches, date__range=[start_date, end_date]
            )

            report_data = {
                "total_health_records": health_records.count(),
                "vaccinations": health_records.filter(
                    record_type="vaccination"
                ).count(),
                "treatments": health_records.filter(record_type="treatment").count(),
                "total_mortality": mortality_records.aggregate(total=Sum("count"))[
                    "total"
                ]
                or 0,
                "health_costs": health_records.aggregate(total=Sum("cost"))["total"]
                or 0,
                "mortality_by_cause": list(
                    mortality_records.values("cause_category")
                    .annotate(total=Sum("count"))
                    .order_by("-total")
                ),
                "batches_included": batches.count(),
                "date_range": f"{start_date} to {end_date}",
            }

        elif report_type == "financial":
            from apps.production.models.models import FeedRecord
            from apps.health.models.models import HealthRecord

            feed_costs = (
                FeedRecord.objects.filter(
                    organization=org,
                    batch__in=batches,
                    date__range=[start_date, end_date],
                ).aggregate(total_cost=Sum(F("quantity_kg") * F("cost_per_kg")))[
                    "total_cost"
                ]
                or 0
            )

            health_costs = (
                HealthRecord.objects.filter(
                    organization=org,
                    batch__in=batches,
                    date__range=[start_date, end_date],
                ).aggregate(total=Sum("cost"))["total"]
                or 0
            )

            total_birds = batches.aggregate(total=Sum("current_count"))["total"] or 0

            report_data = {
                "feed_costs": feed_costs,
                "health_costs": health_costs,
                "total_operational_costs": feed_costs + health_costs,
                "cost_per_bird": (
                    (feed_costs + health_costs) / total_birds if total_birds > 0 else 0
                ),
                "total_birds": total_birds,
                "batches_included": batches.count(),
                "date_range": f"{start_date} to {end_date}",
            }

        report = Report.objects.create(
            title=f"{report_type.title()} Report - {start_date} to {end_date}",
            report_type=report_type,
            report_format="json",
            start_date=start_date,
            end_date=end_date,
            parameters=report_data,
            generated_by=user,
            organization=org,
        )

        if batch_ids:
            report.batches.set(batches)

        return Response(
            {
                "report_id": report.id,
                "report_data": report_data,
                "message": "Report generated successfully",
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_alert_view(request):
    """API view for creating system alerts."""
    org = _get_org(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    batch_id = request.data.get("batch_id")
    alert_type = request.data.get("alert_type")
    severity = request.data.get("severity")
    title = request.data.get("title")
    message = request.data.get("message")

    if not all([alert_type, severity, title, message]):
        return Response(
            {"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = request.user
        batch = None
        if batch_id:
            batch = Batch.objects.get(id=batch_id, organization=org)

        alert = Alert.objects.create(
            batch=batch,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            created_by=user,
            organization=org,
        )

        return Response(
            {
                "alert": AlertSerializer(alert).data,
                "message": "Alert created successfully",
            }
        )

    except Batch.DoesNotExist:
        return Response({"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def bulk_alert_update_view(request):
    """API view for bulk updating alerts (mark as read/resolved)."""
    org = _get_org(request)
    if not org:
        return Response(
            {"error": "No organization selected"}, status=status.HTTP_400_BAD_REQUEST
        )

    alert_ids = request.data.get("alert_ids", [])
    action = request.data.get("action")

    if not alert_ids or not action:
        return Response(
            {"error": "Missing alert_ids or action"}, status=status.HTTP_400_BAD_REQUEST
        )

    alerts = Alert.objects.filter(organization=org, id__in=alert_ids)
    updated_count = 0

    for alert in alerts:
        if action == "mark_read":
            alert.is_read = True
            alert.save()
            updated_count += 1
        elif action == "mark_resolved":
            alert.is_resolved = True
            alert.resolved_by = request.user
            alert.resolved_at = timezone.now()
            alert.save()
            updated_count += 1

    return Response(
        {
            "updated_count": updated_count,
            "message": f"{updated_count} alerts updated successfully",
        }
    )
