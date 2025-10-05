from rest_framework import serializers
from apps.production.models.models import FeedRecord, EggProduction, WeightRecord, EnvironmentalRecord
from apps.users.api.serializers import UserSerializer

class FeedRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for FeedRecord model
    """
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    total_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedRecord
        fields = [
            'id', 'batch', 'batch_id', 'date', 'feed_type', 'brand',
            'quantity_kg', 'cost_per_kg', 'total_cost', 'supplier',
            'batch_number', 'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ('id', 'recorded_by', 'created_at')
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)

class EggProductionSerializer(serializers.ModelSerializer):
    """
    Serializer for EggProduction model
    """
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    production_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = EggProduction
        fields = [
            'id', 'batch', 'batch_id', 'date', 'total_eggs', 'grade_a_eggs',
            'grade_b_eggs', 'grade_c_eggs', 'cracked_eggs', 'dirty_eggs',
            'average_weight', 'production_rate', 'recorded_by',
            'recorded_by_name', 'created_at'
        ]
        read_only_fields = ('id', 'recorded_by', 'created_at')
    
    def validate(self, attrs):
        # Validate that sum of graded eggs equals total eggs
        total_graded = (
            attrs.get('grade_a_eggs', 0) +
            attrs.get('grade_b_eggs', 0) +
            attrs.get('grade_c_eggs', 0) +
            attrs.get('cracked_eggs', 0) +
            attrs.get('dirty_eggs', 0)
        )
        
        if total_graded != attrs.get('total_eggs', 0):
            raise serializers.ValidationError(
                "Sum of graded eggs must equal total eggs"
            )
        
        return attrs
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)

class WeightRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for WeightRecord model
    """
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = WeightRecord
        fields = [
            'id', 'batch', 'batch_id', 'date', 'sample_size', 'average_weight',
            'min_weight', 'max_weight', 'age_in_days', 'notes',
            'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ('id', 'recorded_by', 'created_at')
    
    def validate(self, attrs):
        min_weight = attrs.get('min_weight')
        max_weight = attrs.get('max_weight')
        average_weight = attrs.get('average_weight')
        
        if min_weight and max_weight and min_weight > max_weight:
            raise serializers.ValidationError("Minimum weight cannot be greater than maximum weight")
        
        if min_weight and average_weight and min_weight > average_weight:
            raise serializers.ValidationError("Minimum weight cannot be greater than average weight")
        
        if max_weight and average_weight and max_weight < average_weight:
            raise serializers.ValidationError("Maximum weight cannot be less than average weight")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)

class EnvironmentalRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for EnvironmentalRecord model
    """
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    
    class Meta:
        model = EnvironmentalRecord
        fields = [
            'id', 'batch', 'batch_id', 'date', 'temperature', 'humidity',
            'ammonia_level', 'ventilation_rate', 'lighting_hours', 'notes',
            'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ('id', 'recorded_by', 'created_at')
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)
