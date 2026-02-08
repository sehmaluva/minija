from rest_framework import serializers
from apps.reports.models.models import Report, Alert
from apps.birds.api.serializers import Batch
from apps.users.api.serializers import UserSerializer


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Report model
    """

    generated_by_name = serializers.CharField(
        source="generated_by.full_name", read_only=True
    )
    batch_count = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "report_type",
            "report_format",
            "start_date",
            "end_date",
            "batches",
            "batch_count",
            "file_path",
            "parameters",
            "generated_by",
            "generated_by_name",
            "generated_at",
        ]
        read_only_fields = ("id", "generated_by", "generated_at")

    def get_batch_count(self, obj):
        return obj.batches.count()

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["generated_by"] = request.user
        validated_data["organization"] = getattr(request, "organization", None)
        return super().create(validated_data)


class ReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating reports with validation
    """

    batch_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Report
        fields = [
            "title",
            "report_type",
            "report_format",
            "start_date",
            "end_date",
            "batch_ids",
            "parameters",
        ]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be after end date")

        return attrs

    def create(self, validated_data):
        batches_ids = validated_data.pop("batches_ids", [])
        request = self.context["request"]
        validated_data["generated_by"] = request.user
        validated_data["organization"] = getattr(request, "organization", None)

        report = Report.objects.create(**validated_data)

        if batches_ids:
            from apps.birds.models.models import Batch

            batches = Batch.objects.filter(id__in=batches_ids)
            report.batches.set(batches)

        return report


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Alert model
    """

    batch_id = serializers.CharField(source="batch.batch_id", read_only=True)
    resolved_by_name = serializers.CharField(
        source="resolved_by.full_name", read_only=True
    )

    class Meta:
        model = Alert
        fields = [
            "id",
            "batch",
            "batch_id",
            "alert_type",
            "severity",
            "title",
            "message",
            "is_read",
            "is_resolved",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "created_by",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "created_by")
        read_only_fields = ("id", "created_at")


class AlertUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating alert status
    """

    class Meta:
        model = Alert
        fields = ["is_read", "is_resolved"]

    def update(self, instance, validated_data):
        if validated_data.get("is_resolved") and not instance.is_resolved:
            from django.utils import timezone

            instance.resolved_by = self.context["request"].user
            instance.resolved_at = timezone.now()

        return super().update(instance, validated_data)
