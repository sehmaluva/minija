from rest_framework import serializers
from apps.birds.models.models import Breed, Flock, FlockMovement, Batch
from apps.users.api.serializers import UserSerializer

class BatchSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    age_in_days = serializers.ReadOnlyField()
    mortality_rate = serializers.ReadOnlyField()
    age_in_weeks = serializers.SerializerMethodField()
    survival_rate = serializers.SerializerMethodField()
    class Meta:
        model = Batch
        exclude = ['id']

    def get_age_in_weeks(self, obj):
        return round(obj.age_in_days / 7, 1)
    
    def get_survival_rate(self, obj):
        if obj.initial_count == 0:
            return 0
        return round((obj.current_count / obj.initial_count) * 100, 2)
    
    def validate(self, attrs):
        # Validate that current_count doesn't exceed initial_count
        current_count = attrs.get('current_count')
        initial_count = attrs.get('initial_count')
        
        if self.instance:
            current_count = current_count or self.instance.current_count
            initial_count = initial_count or self.instance.initial_count
        
        if current_count and initial_count and current_count > initial_count:
            raise serializers.ValidationError("Current count cannot exceed initial count")
        
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
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class BatchSummarySerializer(serializers.ModelSerializer):
    age_in_weeks = serializers.SerializerMethodField()
    survival_rate = serializers.SerializerMethodField()
    class Meta:
        model = Batch
        fields = [
            'id', 'batch_number', 'current_count', 'age_in_weeks', 'survival_rate'
        ]
    
    def get_age_in_weeks(self, obj):
        return round(obj.age_in_days / 7, 1)
    
    def get_survival_rate(self, obj):
        if obj.initial_count == 0:
            return 0
        return round((obj.current_count / obj.initial_count) * 100, 2)
      
class BreedSerializer(serializers.ModelSerializer):
    """
    Serializer for Breed model
    """
    total_flocks = serializers.SerializerMethodField()
    
    class Meta:
        model = Breed
        fields = [
            'id', 'name', 'species', 'description', 'average_weight',
            'egg_production_rate', 'maturity_age', 'created_at', 'total_flocks'
        ]
        read_only_fields = ('id', 'created_at')
    
    def get_total_flocks(self, obj):
        return obj.flocks.filter(status='active').count()

class FlockSerializer(serializers.ModelSerializer):
    """Serializer for Flock model (farm/building removed)."""
    breed_name = serializers.CharField(source='breed.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    age_in_days = serializers.ReadOnlyField()
    mortality_rate = serializers.ReadOnlyField()
    age_in_weeks = serializers.SerializerMethodField()
    survival_rate = serializers.SerializerMethodField()
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Flock
        fields = [
            'id', 'breed', 'breed_name', 'flock_id', 'flock_type', 'initial_count',
            'current_count', 'hatch_date', 'source', 'status', 'notes', 'location',
            'created_by', 'created_by_name', 'created_at', 'updated_at', 'age_in_days',
            'age_in_weeks', 'mortality_rate', 'survival_rate'
        ]
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_age_in_weeks(self, obj):
        return round(obj.age_in_days / 7, 1)
    
    def get_survival_rate(self, obj):
        if obj.initial_count == 0:
            return 0
        return round((obj.current_count / obj.initial_count) * 100, 2)
    
    def validate(self, attrs):
        # Validate that current_count doesn't exceed initial_count
        current_count = attrs.get('current_count')
        initial_count = attrs.get('initial_count')
        
        if self.instance:
            current_count = current_count or self.instance.current_count
            initial_count = initial_count or self.instance.initial_count
        
        if current_count and initial_count and current_count > initial_count:
            raise serializers.ValidationError("Current count cannot exceed initial count")
        
        # Building capacity validation removed
        
        return attrs
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class FlockMovementSerializer(serializers.ModelSerializer):
    """Serializer for FlockMovement model (building removed)."""
    flock_id = serializers.CharField(source='flock.flock_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    from_location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    to_location = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = FlockMovement
        fields = [
            'id', 'flock', 'flock_id', 'movement_type', 'from_location', 'to_location',
            'bird_count', 'movement_date', 'reason', 'recorded_by', 'recorded_by_name', 'created_at'
        ]
        read_only_fields = ('id', 'recorded_by', 'created_at')
    
    def validate(self, attrs):
        flock = attrs.get('flock')
        bird_count = attrs.get('bird_count')
        movement_type = attrs.get('movement_type')
        
        # Validate bird count doesn't exceed current flock count
        if flock and bird_count and bird_count > flock.current_count:
            raise serializers.ValidationError(
                f"Bird count ({bird_count}) exceeds current flock count ({flock.current_count})"
            )
        
        # No building capacity validation anymore
        
        return attrs
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        movement = super().create(validated_data)
        
        # Update flock count based on movement type
        flock = movement.flock
        if movement.movement_type in ['sale', 'processing', 'mortality', 'culling']:
            flock.current_count -= movement.bird_count
            if flock.current_count <= 0:
                flock.status = movement.movement_type
                flock.current_count = 0
        elif movement.movement_type == 'transfer' and movement.to_location:
            flock.location = movement.to_location
        
        flock.save()
        return movement

class FlockSummarySerializer(serializers.ModelSerializer):
    """Serializer for Flock summary (no building)."""
    breed_name = serializers.CharField(source='breed.name', read_only=True)
    age_in_weeks = serializers.SerializerMethodField()
    survival_rate = serializers.SerializerMethodField()

    class Meta:
        model = Flock
        fields = [
            'id', 'flock_id', 'flock_type', 'breed_name', 'current_count', 'age_in_weeks', 'survival_rate', 'status', 'location'
        ]
    
    def get_age_in_weeks(self, obj):
        return round(obj.age_in_days / 7, 1)
    
    def get_survival_rate(self, obj):
        if obj.initial_count == 0:
            return 0
        return round((obj.current_count / obj.initial_count) * 100, 2)
