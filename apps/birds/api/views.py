from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Avg, Q
from django.utils import timezone
from apps.birds.models.models import Batch, Breed, Flock, FlockMovement
from apps.birds.api.serializers import (
    BreedSerializer, FlockSerializer, FlockMovementSerializer, FlockSummarySerializer, BatchSerializer
)
from apps.users.permissions import CanManageFlocks, CanManageBatches

class BatchListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating batches"""
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['batch_number',]
    ordering_fields = ['batch_id', 'current_count', 'collection_date', 'created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == "admin":
            return Batch.objects.all()
        else:
            return Batch.objects.filter(created_by=user).distinct()
        
class BatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == "admin":
            return Batch.objects.all()
        else:
            return Batch.objects.filter(created_by=user).distinct()
        
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageBatches()]
        return [permissions.IsAuthenticated()]
    
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def batch_statistics_view(request):
    """
    API view for getting batch statistics
    """
    user = request.user
    
    if getattr(user, 'role', None) == 'admin':
        batches = Batch.objects.all()
    else:
        batches = Batch.objects.filter(created_by=user).distinct()
        
    active_batches = batches.filter(status='active')
    
    stats = {
        'total_flocks': batches.count(),
        'active_batches': active_batches.count(),
        'total_birds': active_batches.aggregate(total=Sum('current_count'))['total'] or 0,
        'average_batch_size': active_batches.aggregate(avg=Avg('current_count'))['avg'] or 0,
        'mortality_stats': {}
    }
    
    all_batches = batches.exclude(status='active')
    for status, _ in Batch.STATUS_CHOICES:
        if status != 'active':
            count = all_batches.filter(status=status).count()
            if count > 0:
                stats['mortality_stats'][status] = count
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def batch_performance_view(request, batch_id):
    """
    API view for getting detailed batch performance metrics
    """
    try:
        user = request.user
        
        if getattr(user, 'role', None) in ['admin']:
            batch = Batch.objects.get(id=batch_id)
        else:
            batch = Batch.objects.get(
                created_by=user,
                id=batch_id
            )
        
        # calculate performance metrics
        age_weeks = batch.age_in_days / 7
        survival_rate = (batch.current_count / batch.initial_count * 100) if batch.initial_count > 0 else 0
        
        # Get weight records
        weight_data = []
        # TODO: Add weight record aggregation once model exists
        
        performance_data = {
            'batch': BatchSerializer(batch).data,
            'metrics': {
                'age_weeks': round(age_weeks, 1),
                'survival_rate': round(survival_rate, 2),
                'mortality_rate': round(100 - survival_rate, 2),
                'birds_lost': batch.initial_count - batch.current_count,
            },
            'weight_data': weight_data
        }
        
        return Response(performance_data)
        
    except Batch.DoesNotExist:
        return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([CanManageFlocks])
def bulk_batch_update_view(request):
    """
    API view for bulk updating batch counts (for mortality, sales, etc.)
    """
    batch_updates = request.data.get('batch_updates', [])
    
    if not batch_updates:
        return Response({'error': 'No batch updates provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    updated_batches = []
    errors = []
    
    for update in batch_updates:
        try:
            batch_id =update.get('batch_id')
            new_count = update.get('new_count')
            reason = update.get('reason')
            
            batch = Batch.objects.get(id=batch_id)
            
            batch.current_count = new_count
            if new_count <= 0:
                batch.status = 'deceased'
            batch.save()
            
            updated_batches.append(BatchSerializer(batch).data)
            
        except Batch.DoesNotExist:
            errors.append(f'Batch with id (batch_id) not found')
        except Exception as e:
            errors.append(f'Error updating batch {batch_id}: {str(e)}')
    
    return Response({
    'updated_batches': updated_batches,
    'errors':errors
    })
            
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
    """API view for listing and creating flocks (farm/building removed)."""
    serializer_class = FlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['flock_type', 'status', 'breed', 'location']
    search_fields = ['flock_id', 'breed__name', 'location']
    ordering_fields = ['flock_id', 'hatch_date', 'current_count', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) in ['admin']:
            return Flock.objects.all()
        return Flock.objects.filter(created_by=user).distinct()

class FlockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting a flock"""
    serializer_class = FlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) in ['admin']:
            return Flock.objects.all()
        return Flock.objects.filter(created_by=user).distinct()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageFlocks()]
        return [permissions.IsAuthenticated()]

class FlockMovementListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating flock movements (farm/building removed)."""
    serializer_class = FlockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['movement_type', 'flock', 'movement_date']
    search_fields = ['flock__flock_id', 'reason', 'from_location', 'to_location']
    ordering_fields = ['movement_date', 'created_at']
    ordering = ['-movement_date']

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) in ['admin']:
            return FlockMovement.objects.all()
        return FlockMovement.objects.filter(
            Q(recorded_by=user) | Q(flock__created_by=user)
        ).distinct()

class FlockMovementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting a flock movement"""
    serializer_class = FlockMovementSerializer
    permission_classes = [CanManageFlocks]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) in ['admin']:
            return FlockMovement.objects.all()
        return FlockMovement.objects.filter(
            Q(recorded_by=user) | Q(flock__created_by=user)
        ).distinct()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def flock_statistics_view(request):
    """
    API view for getting flock statistics
    """
    user = request.user
    
    if getattr(user, 'role', None) in ['admin']:
        flocks = Flock.objects.all()
    else:
        flocks = Flock.objects.filter(created_by=user).distinct()
    
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

        if getattr(user, 'role', None) in ['admin']:
            flock = Flock.objects.get(id=flock_id)
        else:
            flock = Flock.objects.get(created_by=user, id=flock_id)

        age_weeks = flock.age_in_days / 7
        survival_rate = (flock.current_count / flock.initial_count * 100) if flock.initial_count > 0 else 0

        # Movements (may be empty if no related name yet after reset)
        recent_movements_qs = FlockMovement.objects.filter(flock=flock).order_by('-movement_date')[:10]

        production_data = []  # placeholder until production models refactored
        weight_data = []      # placeholder until weight tracking added

        performance_data = {
            'flock': FlockSerializer(flock).data,
            'metrics': {
                'age_weeks': round(age_weeks, 1),
                'survival_rate': round(survival_rate, 2),
                'mortality_rate': round(100 - survival_rate, 2),
                'birds_lost': flock.initial_count - flock.current_count,
            },
            'recent_movements': FlockMovementSerializer(recent_movements_qs, many=True).data if recent_movements_qs else [],
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
