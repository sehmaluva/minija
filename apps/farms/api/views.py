from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.farms.models.models import Farm, Building
from apps.farms.api.serializers import FarmSerializer, BuildingSerializer, FarmSummarySerializer
from apps.users.permissions import IsOwnerOrManager, IsAdminOrOwner

class FarmListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating farms
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'state', 'country']
    search_fields = ['name', 'city', 'license_number']
    ordering_fields = ['name', 'created_at', 'established_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return Farm.objects.all()
        elif user.role in ['owner', 'manager']:
            return Farm.objects.filter(
                models.Q(owner=user) | models.Q(managers=user)
            ).distinct()
        else:
            # Workers can only see farms they're associated with through flocks
            return Farm.objects.filter(
                flocks__created_by=user
            ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class FarmDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting a farm
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return Farm.objects.all()
        elif user.role in ['owner', 'manager']:
            from django.db import models
            return Farm.objects.filter(
                models.Q(owner=user) | models.Q(managers=user)
            ).distinct()
        else:
            return Farm.objects.filter(
                flocks__created_by=user
            ).distinct()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsOwnerOrManager()]
        return [permissions.IsAuthenticated()]

class BuildingListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating buildings
    """
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['building_type', 'is_active', 'farm']
    search_fields = ['name', 'farm__name']
    ordering_fields = ['name', 'capacity', 'construction_date']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return Building.objects.all()
        else:
            from django.db import models
            return Building.objects.filter(
                models.Q(farm__owner=user) | 
                models.Q(farm__managers=user) |
                models.Q(farm__flocks__created_by=user)
            ).distinct()

class BuildingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting a building
    """
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return Building.objects.all()
        else:
            from django.db import models
            return Building.objects.filter(
                models.Q(farm__owner=user) | 
                models.Q(farm__managers=user) |
                models.Q(farm__flocks__created_by=user)
            ).distinct()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsOwnerOrManager()]
        return [permissions.IsAuthenticated()]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def farm_summary_view(request):
    """
    API view for getting farm summary statistics
    """
    user = request.user
    
    if user.role in ['admin']:
        farms = Farm.objects.filter(is_active=True)
    else:
        from django.db import models
        farms = Farm.objects.filter(
            models.Q(owner=user) | models.Q(managers=user),
            is_active=True
        ).distinct()
    
    total_farms = farms.count()
    total_buildings = sum(farm.buildings.filter(is_active=True).count() for farm in farms)
    total_flocks = sum(farm.flocks.filter(status='active').count() for farm in farms)
    total_birds = sum(
        sum(flock.current_count for flock in farm.flocks.filter(status='active'))
        for farm in farms
    )
    
    return Response({
        'total_farms': total_farms,
        'total_buildings': total_buildings,
        'total_flocks': total_flocks,
        'total_birds': total_birds,
        'farms': FarmSummarySerializer(farms, many=True).data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def building_occupancy_view(request, farm_id):
    """
    API view for getting building occupancy for a specific farm
    """
    try:
        user = request.user
        
        if user.role in ['admin']:
            farm = Farm.objects.get(id=farm_id)
        else:
            from django.db import models
            farm = Farm.objects.get(
                models.Q(owner=user) | models.Q(managers=user),
                id=farm_id
            )
        
        buildings = farm.buildings.filter(is_active=True)
        building_data = []
        
        for building in buildings:
            current_occupancy = sum(flock.current_count for flock in building.flocks.filter(status='active'))
            occupancy_rate = (current_occupancy / building.capacity * 100) if building.capacity > 0 else 0
            
            building_data.append({
                'id': building.id,
                'name': building.name,
                'building_type': building.building_type,
                'capacity': building.capacity,
                'current_occupancy': current_occupancy,
                'occupancy_rate': round(occupancy_rate, 2),
                'available_space': building.capacity - current_occupancy
            })
        
        return Response({
            'farm_name': farm.name,
            'buildings': building_data
        })
        
    except Farm.DoesNotExist:
        return Response({'error': 'Farm not found'}, status=status.HTTP_404_NOT_FOUND)
