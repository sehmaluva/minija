from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from apps.health.models.models import HealthRecord, MortalityRecord
from .serializers import (
    HealthRecordSerializer, HealthRecordCreateSerializer, MortalityRecordSerializer
)
from apps.users.permissions import IsVeterinarianOrManager

class HealthRecordListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating health records
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['record_type', 'flock', 'date', 'veterinarian']
    search_fields = ['description', 'flock__flock_id']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HealthRecordCreateSerializer
        return HealthRecordSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return HealthRecord.objects.all()
        elif user.role in ['veterinarian']:
            return HealthRecord.objects.filter(
                Q(veterinarian=user) | Q(created_by=user)
            )
        else:
            return HealthRecord.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(created_by=user)
            ).distinct()

class HealthRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting a health record
    """
    serializer_class = HealthRecordSerializer
    permission_classes = [IsVeterinarianOrManager]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return HealthRecord.objects.all()
        elif user.role in ['veterinarian']:
            return HealthRecord.objects.filter(
                Q(veterinarian=user) | Q(created_by=user)
            )
        else:
            return HealthRecord.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(created_by=user)
            ).distinct()

class MortalityRecordListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating mortality records
    """
    serializer_class = MortalityRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['cause_category', 'flock', 'date']
    search_fields = ['specific_cause', 'flock__flock_id']
    ordering_fields = ['date', 'count', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return MortalityRecord.objects.all()
        else:
            return MortalityRecord.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

class MortalityRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting a mortality record
    """
    serializer_class = MortalityRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return MortalityRecord.objects.all()
        else:
            return MortalityRecord.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def health_dashboard_view(request):
    """
    API view for health dashboard statistics
    """
    user = request.user
    
    # Get user's accessible flocks
    if user.role in ['admin']:
        from flocks.models import Flock
        flocks = Flock.objects.filter(status='active')
    else:
        from flocks.models import Flock
        flocks = Flock.objects.filter(
            Q(farm__owner=user) | 
            Q(farm__managers=user) |
            Q(created_by=user),
            status='active'
        ).distinct()
    
    # Recent health records
    recent_records = HealthRecord.objects.filter(
        flock__in=flocks
    ).order_by('-date')[:10]
    
    # Vaccination schedule (upcoming)
    upcoming_vaccinations = HealthRecord.objects.filter(
        flock__in=flocks,
        record_type='vaccination',
        vaccination_details__next_vaccination_date__gte=timezone.now().date(),
        vaccination_details__next_vaccination_date__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('vaccination_details__next_vaccination_date')
    
    # Mortality statistics (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_mortality = MortalityRecord.objects.filter(
        flock__in=flocks,
        date__gte=thirty_days_ago
    )
    
    mortality_by_cause = recent_mortality.values('cause_category').annotate(
        total_count=Sum('count')
    ).order_by('-total_count')
    
    # Health alerts
    alerts = []
    
    # High mortality rate alert
    for flock in flocks:
        recent_flock_mortality = recent_mortality.filter(flock=flock).aggregate(
            total=Sum('count')
        )['total'] or 0
        
        if recent_flock_mortality > 0:
            mortality_rate = (recent_flock_mortality / flock.current_count) * 100
            if mortality_rate > 5:  # Alert if mortality rate > 5% in 30 days
                alerts.append({
                    'type': 'high_mortality',
                    'flock_id': flock.flock_id,
                    'message': f'High mortality rate: {mortality_rate:.1f}% in last 30 days',
                    'severity': 'high' if mortality_rate > 10 else 'medium'
                })
    
    dashboard_data = {
        'recent_health_records': HealthRecordSerializer(recent_records, many=True).data,
        'upcoming_vaccinations': HealthRecordSerializer(upcoming_vaccinations, many=True).data,
        'mortality_statistics': {
            'total_deaths_30_days': recent_mortality.aggregate(total=Sum('count'))['total'] or 0,
            'by_cause': list(mortality_by_cause),
            'average_age_at_death': recent_mortality.aggregate(avg=Avg('age_at_death'))['avg'] or 0
        },
        'health_alerts': alerts,
        'summary': {
            'total_active_flocks': flocks.count(),
            'total_health_records': HealthRecord.objects.filter(flock__in=flocks).count(),
            'vaccinations_this_month': HealthRecord.objects.filter(
                flock__in=flocks,
                record_type='vaccination',
                date__gte=timezone.now().date().replace(day=1)
            ).count()
        }
    }
    
    return Response(dashboard_data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def flock_health_history_view(request, flock_id):
    """
    API view for getting complete health history of a flock
    """
    try:
        user = request.user
        
        if user.role in ['admin']:
            from flocks.models import Flock
            flock = Flock.objects.get(id=flock_id)
        else:
            from flocks.models import Flock
            flock = Flock.objects.get(
                Q(farm__owner=user) | 
                Q(farm__managers=user) |
                Q(created_by=user),
                id=flock_id
            )
        
        # Get all health records
        health_records = flock.health_records.all().order_by('-date')
        
        # Get mortality records
        mortality_records = flock.mortality_records.all().order_by('-date')
        
        # Calculate health metrics
        total_vaccinations = health_records.filter(record_type='vaccination').count()
        total_treatments = health_records.filter(record_type='treatment').count()
        total_deaths = mortality_records.aggregate(total=Sum('count'))['total'] or 0
        
        health_history = {
            'flock': {
                'id': flock.id,
                'flock_id': flock.flock_id,
                'breed': flock.breed.name,
                'current_count': flock.current_count,
                'age_in_days': flock.age_in_days
            },
            'health_records': HealthRecordSerializer(health_records, many=True).data,
            'mortality_records': MortalityRecordSerializer(mortality_records, many=True).data,
            'health_metrics': {
                'total_vaccinations': total_vaccinations,
                'total_treatments': total_treatments,
                'total_deaths': total_deaths,
                'mortality_rate': (total_deaths / flock.initial_count * 100) if flock.initial_count > 0 else 0,
                'health_cost': health_records.aggregate(total=Sum('cost'))['total'] or 0
            }
        }
        
        return Response(health_history)
        
    except:
        from flocks.models import Flock
        return Response({'error': 'Flock not found'}, status=status.HTTP_404_NOT_FOUND)
