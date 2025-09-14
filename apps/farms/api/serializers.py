from rest_framework import serializers
from apps.farms.models.models import Farm, Building
from apps.users.api.serializers import UserSerializer

class FarmSerializer(serializers.ModelSerializer):
    """
    Serializer for Farm model
    """
    owner = UserSerializer(read_only=True)
    managers = UserSerializer(many=True, read_only=True)
    manager_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    total_buildings = serializers.SerializerMethodField()
    total_capacity = serializers.SerializerMethodField()
    
    class Meta:
        model = Farm
        fields = [
            'id', 'name', 'description', 'address', 'city', 'state', 'country',
            'postal_code', 'phone_number', 'email', 'license_number',
            'established_date', 'total_area', 'owner', 'managers', 'manager_ids',
            'is_active', 'created_at', 'updated_at', 'total_buildings', 'total_capacity'
        ]
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
    
    def get_total_buildings(self, obj):
        return obj.buildings.filter(is_active=True).count()
    
    def get_total_capacity(self, obj):
        return sum(building.capacity for building in obj.buildings.filter(is_active=True))
    
    def create(self, validated_data):
        manager_ids = validated_data.pop('manager_ids', [])
        farm = Farm.objects.create(**validated_data)
        
        if manager_ids:
            from users.models import User
            managers = User.objects.filter(id__in=manager_ids, role__in=['manager', 'admin'])
            farm.managers.set(managers)
        
        return farm
    
    def update(self, instance, validated_data):
        manager_ids = validated_data.pop('manager_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if manager_ids is not None:
            from users.models import User
            managers = User.objects.filter(id__in=manager_ids, role__in=['manager', 'admin'])
            instance.managers.set(managers)
        
        return instance

class BuildingSerializer(serializers.ModelSerializer):
    """
    Serializer for Building model
    """
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    area = serializers.ReadOnlyField()
    current_occupancy = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Building
        fields = [
            'id', 'farm', 'farm_name', 'name', 'building_type', 'capacity',
            'length', 'width', 'height', 'area', 'construction_date',
            'is_active', 'notes', 'created_at', 'updated_at',
            'current_occupancy', 'occupancy_rate'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_current_occupancy(self, obj):
        return sum(flock.current_count for flock in obj.flocks.filter(status='active'))
    
    def get_occupancy_rate(self, obj):
        current_occupancy = self.get_current_occupancy(obj)
        if obj.capacity == 0:
            return 0
        return (current_occupancy / obj.capacity) * 100

class FarmSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for Farm summary with basic info
    """
    total_buildings = serializers.SerializerMethodField()
    total_flocks = serializers.SerializerMethodField()
    total_birds = serializers.SerializerMethodField()
    
    class Meta:
        model = Farm
        fields = ['id', 'name', 'city', 'state', 'total_buildings', 'total_flocks', 'total_birds']
    
    def get_total_buildings(self, obj):
        return obj.buildings.filter(is_active=True).count()
    
    def get_total_flocks(self, obj):
        return obj.flocks.filter(status='active').count()
    
    def get_total_birds(self, obj):
        return sum(flock.current_count for flock in obj.flocks.filter(status='active'))
