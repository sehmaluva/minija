from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum, Avg
from apps.flocks.models.models import Breed, Flock, FlockMovement
from apps.flocks.api.serializers import (
    BreedSerializer, FlockSerializer, FlockMovementSerializer, FlockSummarySerializer
)
from apps.users.permissions import CanManageFlocks

class BreedListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating breeds
    """
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'species']
    ordering_fields = ['name', 'species', 'created_at']
    ordering = ['name']

class BreedDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting a breed
    """
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [CanManageFlocks]

class FlockListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating flocks
    """
    serializer_class = FlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['flock_type', 'status', 'farm', 'building', 'breed']
    search_fields = ['flock_id', 'breed__name', 'farm__name', 'building__name']
    ordering_fields = ['flock_id', 'hatch_date', 'current_count', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return Flock.objects.all()
        else:
            return Flock.objects.filter(
                Q(farm__owner=user) | 
                Q(farm__managers=user) |
                Q(created_by=user)
            ).distinct()

class FlockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting a flock
    """
    serializer_class = FlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return Flock.objects.all()
        else:
            return Flock.objects.filter(
                Q(farm__owner=user) | 
                Q(farm__managers=user) |
                Q(created_by=user)
            ).distinct()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageFlocks()]
        return [permissions.IsAuthenticated()]

class FlockMovementListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating flock movements
    """
    serializer_class = FlockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['movement_type', 'flock', 'movement_date']
    search_fields = ['flock__flock_id', 'reason']
    ordering_fields = ['movement_date', 'created_at']
    ordering = ['-movement_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return FlockMovement.objects.all()
        else:
            return FlockMovement.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

class FlockMovementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting a flock movement
    """
    serializer_class = FlockMovementSerializer
    permission_classes = [CanManageFlocks]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return FlockMovement.objects.all()
        else:
            return FlockMovement.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def flock_statistics_view(request):
    """
    API view for getting flock statistics
    """
    user = request.user
    
    if user.role in ['admin']:
        flocks = Flock.objects.all()
    else:
        flocks = Flock.objects.filter(
            Q(farm__owner=user) | 
            Q(farm__managers=user) |
            Q(created_by=user)
        ).distinct()
    
    active_flocks = flocks.filter(status='active')
    
    stats = {
        'total_flocks': flocks.count(),
        'active_flocks': active_flocks.count(),
        'total_birds': active_flocks.aggregate(total=Sum('current_count'))['total'] or 0,
        'average_flock_size': active_flocks.aggregate(avg=Avg('current_count'))['avg'] or 0,
        'flock_types': {},
        'breeds': {},
        'mortality_stats': {}
    }
    
    # Flock type distribution
    for flock_type, _ in Flock.FLOCK_TYPES:
        count = active_flocks.filter(flock_type=flock_type).count()
        if count > 0:
            stats['flock_types'][flock_type] = count
    
    # Breed distribution
    breed_stats = active_flocks.values('breed__name').annotate(
        count=Sum('current_count')
    ).order_by('-count')[:5]
    
    for breed_stat in breed_stats:
        stats['breeds'][breed_stat['breed__name']] = breed_stat['count']
    
    # Mortality statistics
    all_flocks = flocks.exclude(status='active')
    for status, _ in Flock.STATUS_CHOICES:
        if status != 'active':
            count = all_flocks.filter(status=status).count()
            if count > 0:
                stats['mortality_stats'][status] = count
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def flock_performance_view(request, flock_id):
    """
    API view for getting detailed flock performance metrics
    """
    try:
        user = request.user
        
        if user.role in ['admin']:
            flock = Flock.objects.get(id=flock_id)
        else:
            flock = Flock.objects.get(
                Q(farm__owner=user) | 
                Q(farm__managers=user) |
                Q(created_by=user),
                id=flock_id
            )
        
        # Calculate performance metrics
        age_weeks = flock.age_in_days / 7
        survival_rate = (flock.current_count / flock.initial_count * 100) if flock.initial_count > 0 else 0
        
        # Get recent movements
        recent_movements = flock.movements.all()[:10]
        
        # Get production data if it's a layer flock
        production_data = []
        if flock.flock_type in ['layer', 'breeder']:
            production_records = flock.egg_productions.all()[:30]
            for record in production_records:
                production_data.append({
                    'date': record.date,
                    'total_eggs': record.total_eggs,
                    'production_rate': record.production_rate
                })
        
        # Get weight records
        weight_data = []
        weight_records = flock.weight_records.all()[:10]
        for record in weight_records:
            weight_data.append({
                'date': record.date,
                'average_weight': record.average_weight,
                'age_in_days': record.age_in_days
            })
        
        performance_data = {
            'flock': FlockSerializer(flock).data,
            'metrics': {
                'age_weeks': round(age_weeks, 1),
                'survival_rate': round(survival_rate, 2),
                'mortality_rate': round(100 - survival_rate, 2),
                'birds_lost': flock.initial_count - flock.current_count,
            },
            'recent_movements': FlockMovementSerializer(recent_movements, many=True).data,
            'production_data': production_data,
            'weight_data': weight_data
        }
        
        return Response(performance_data)
        
    except Flock.DoesNotExist:
        return Response({'error': 'Flock not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([CanManageFlocks])
def bulk_flock_update_view(request):
    """
    API view for bulk updating flock counts (for mortality, sales, etc.)
    """
    flock_updates = request.data.get('flock_updates', [])
    
    if not flock_updates:
        return Response({'error': 'No flock updates provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    updated_flocks = []
    errors = []
    
    for update in flock_updates:
        try:
            flock_id = update.get('flock_id')
            new_count = update.get('new_count')
            reason = update.get('reason', '')
            
            flock = Flock.objects.get(id=flock_id)
            
            # Create movement record
            if new_count < flock.current_count:
                movement_count = flock.current_count - new_count
                FlockMovement.objects.create(
                    flock=flock,
                    movement_type='mortality',
                    bird_count=movement_count,
                    movement_date=timezone.now(),
                    reason=reason,
                    recorded_by=request.user
                )
            
            flock.current_count = new_count
            if new_count <= 0:
                flock.status = 'deceased'
            flock.save()
            
            updated_flocks.append(FlockSerializer(flock).data)
            
        except Flock.DoesNotExist:
            errors.append(f"Flock with ID {flock_id} not found")
        except Exception as e:
            errors.append(f"Error updating flock {flock_id}: {str(e)}")
    
    return Response({
        'updated_flocks': updated_flocks,
        'errors': errors
    })
