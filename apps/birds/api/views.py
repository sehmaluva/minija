from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Avg, Q
from django.utils import timezone
from apps.birds.models.models import Batch
from apps.birds.api.serializers import BatchSerializer
from apps.users.permissions import CanManageBatches

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
@permission_classes([CanManageBatches])
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
