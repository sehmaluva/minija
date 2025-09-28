from rest_framework import serializers
from apps.reports.models.models import Report, Alert
from apps.farms.api.serializers import FarmSerializer
from apps.birds.api.serializers import FlockSerializer
from apps.users.api.serializers import UserSerializer

class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Report model
    """
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    flocks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'farm', 'farm_name', 'title', 'report_type', 'report_format',
            'start_date', 'end_date', 'flocks', 'flocks_count', 'file_path',
            'parameters', 'generated_by', 'generated_by_name', 'generated_at'
        ]
        read_only_fields = ('id', 'generated_by', 'generated_at')
    
    def get_flocks_count(self, obj):
        return obj.flocks.count()
    
    def create(self, validated_data):
        validated_data['generated_by'] = self.context['request'].user
        return super().create(validated_data)

class ReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating reports with validation
    """
    flock_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Report
        fields = [
            'farm', 'title', 'report_type', 'report_format',
            'start_date', 'end_date', 'flock_ids', 'parameters'
        ]
    
    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be after end date")
        
        return attrs
    
    def create(self, validated_data):
        flock_ids = validated_data.pop('flock_ids', [])
        validated_data['generated_by'] = self.context['request'].user
        
        report = Report.objects.create(**validated_data)
        
        if flock_ids:
            from apps.birds.models.models import Flock
            flocks = Flock.objects.filter(id__in=flock_ids, farm=report.farm)
            report.flocks.set(flocks)
        
        return report

class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Alert model
    """
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    flock_id = serializers.CharField(source='flock.flock_id', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.full_name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'farm', 'farm_name', 'flock', 'flock_id', 'alert_type',
            'severity', 'title', 'message', 'is_read', 'is_resolved',
            'resolved_by', 'resolved_by_name', 'resolved_at', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')

class AlertUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating alert status
    """
    class Meta:
        model = Alert
        fields = ['is_read', 'is_resolved']
    
    def update(self, instance, validated_data):
        if validated_data.get('is_resolved') and not instance.is_resolved:
            from django.utils import timezone
            instance.resolved_by = self.context['request'].user
            instance.resolved_at = timezone.now()
        
        return super().update(instance, validated_data)
