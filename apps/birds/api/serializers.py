from rest_framework import serializers
from apps.birds.models.models import Batch
from apps.users.api.serializers import UserSerializer


class BatchSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )
    age_in_days = serializers.ReadOnlyField()
    mortality_rate = serializers.ReadOnlyField()
    age_in_weeks = serializers.SerializerMethodField()
    survival_rate = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        exclude = ["id"]

    def get_age_in_weeks(self, obj):
        return round(obj.age_in_days / 7, 1)

    def get_survival_rate(self, obj):
        if obj.initial_count == 0:
            return 0
        return round((obj.current_count / obj.initial_count) * 100, 2)

    def validate(self, attrs):
        # Validate that current_count doesn't exceed initial_count
        current_count = attrs.get("current_count")
        initial_count = attrs.get("initial_count")

        if self.instance:
            current_count = current_count or self.instance.current_count
            initial_count = initial_count or self.instance.initial_count

        if current_count and initial_count and current_count > initial_count:
            raise serializers.ValidationError(
                "Current count cannot exceed initial count"
            )

        # # Validate building capacity
        # building = attrs.get('building')
        # if building and current_count:
        #     existing_birds = sum(
        #         flock.current_count for flock in building.flocks.filter(status='active')
        #         if flock != self.instance
        #     )
        #     if existing_birds + current_count > building.capacity:
        #         raise serializers.ValidationError(
        #             f"Building capacity exceeded. Available space: {building.capacity - existing_birds}"
        #         )

        return attrs

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class BatchSummarySerializer(serializers.ModelSerializer):
    age_in_weeks = serializers.SerializerMethodField()
    survival_rate = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = [
            "id",
            "batch_number",
            "current_count",
            "age_in_weeks",
            "survival_rate",
        ]

    def get_age_in_weeks(self, obj):
        return round(obj.age_in_days / 7, 1)

    def get_survival_rate(self, obj):
        if obj.initial_count == 0:
            return 0
        return round((obj.current_count / obj.initial_count) * 100, 2)
