from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from apps.production.models.models import FeedRecord, EggProduction, WeightRecord, EnvironmentalRecord
from apps.production.api.serializers import (
    FeedRecordSerializer, EggProductionSerializer, 
    WeightRecordSerializer, EnvironmentalRecordSerializer
)

class FeedRecordListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating feed records
    """
    serializer_class = FeedRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['feed_type', 'flock', 'date', 'brand']
    search_fields = ['brand', 'supplier', 'flock__flock_id']
    ordering_fields = ['date', 'quantity_kg', 'cost_per_kg']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return FeedRecord.objects.all()
        else:
            return FeedRecord.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

class EggProductionListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating egg production records
    """
    serializer_class = EggProductionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['flock', 'date']
    search_fields = ['flock__flock_id']
    ordering_fields = ['date', 'total_eggs', 'production_rate']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return EggProduction.objects.all()
        else:
            return EggProduction.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

class WeightRecordListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating weight records
    """
    serializer_class = WeightRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['flock', 'date']
    search_fields = ['flock__flock_id']
    ordering_fields = ['date', 'average_weight', 'age_in_days']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return WeightRecord.objects.all()
        else:
            return WeightRecord.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

class EnvironmentalRecordListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating environmental records
    """
    serializer_class = EnvironmentalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['flock', 'date']
    search_fields = ['flock__flock_id']
    ordering_fields = ['date', 'temperature', 'humidity']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin']:
            return EnvironmentalRecord.objects.all()
        else:
            return EnvironmentalRecord.objects.filter(
                Q(flock__farm__owner=user) | 
                Q(flock__farm__managers=user) |
                Q(recorded_by=user)
            ).distinct()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def production_dashboard_view(request):
    """
    API view for production dashboard statistics
    """
    user = request.user
    
    # Get user's accessible flocks
    if user.role in ['admin']:
        from apps.birds.models.models import Flock
        flocks = Flock.objects.filter(status='active')
    else:
        from apps.birds.models.models import Flock
        flocks = Flock.objects.filter(
            Q(farm__owner=user) | 
            Q(farm__managers=user) |
            Q(created_by=user),
            status='active'
        ).distinct()
    
    # Feed consumption (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_feed = FeedRecord.objects.filter(
        flock__in=flocks,
        date__gte=thirty_days_ago
    )
    
    feed_stats = {
        'total_consumption': recent_feed.aggregate(total=Sum('quantity_kg'))['total'] or 0,
        'total_cost': sum(record.total_cost for record in recent_feed),
        'by_type': recent_feed.values('feed_type').annotate(
            total_kg=Sum('quantity_kg'),
            total_cost=Sum('quantity_kg') * Avg('cost_per_kg')
        ).order_by('-total_kg')
    }
    
    # Egg production (last 30 days) - only for layer flocks
    layer_flocks = flocks.filter(flock_type__in=['layer', 'breeder'])
    recent_eggs = EggProduction.objects.filter(
        flock__in=layer_flocks,
        date__gte=thirty_days_ago
    )
    
    egg_stats = {
        'total_eggs': recent_eggs.aggregate(total=Sum('total_eggs'))['total'] or 0,
        'average_production_rate': recent_eggs.aggregate(avg=Avg('production_rate'))['avg'] or 0,
        'grade_distribution': {
            'grade_a': recent_eggs.aggregate(total=Sum('grade_a_eggs'))['total'] or 0,
            'grade_b': recent_eggs.aggregate(total=Sum('grade_b_eggs'))['total'] or 0,
            'grade_c': recent_eggs.aggregate(total=Sum('grade_c_eggs'))['total'] or 0,
            'cracked': recent_eggs.aggregate(total=Sum('cracked_eggs'))['total'] or 0,
            'dirty': recent_eggs.aggregate(total=Sum('dirty_eggs'))['total'] or 0,
        }
    }
    
    # Weight tracking
    recent_weights = WeightRecord.objects.filter(
        flock__in=flocks,
        date__gte=thirty_days_ago
    )
    
    weight_stats = {
        'average_weight': recent_weights.aggregate(avg=Avg('average_weight'))['avg'] or 0,
        'weight_gain_trend': [],  # This would need more complex calculation
        'records_count': recent_weights.count()
    }
    
    # Environmental conditions
    recent_environmental = EnvironmentalRecord.objects.filter(
        flock__in=flocks,
        date__gte=thirty_days_ago
    )
    
    environmental_stats = {
        'average_temperature': recent_environmental.aggregate(avg=Avg('temperature'))['avg'] or 0,
        'average_humidity': recent_environmental.aggregate(avg=Avg('humidity'))['avg'] or 0,
        'records_count': recent_environmental.count()
    }
    
    dashboard_data = {
        'feed_consumption': feed_stats,
        'egg_production': egg_stats,
        'weight_tracking': weight_stats,
        'environmental_conditions': environmental_stats,
        'summary': {
            'active_flocks': flocks.count(),
            'layer_flocks': layer_flocks.count(),
            'total_birds': flocks.aggregate(total=Sum('current_count'))['total'] or 0
        }
    }
    
    return Response(dashboard_data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def flock_production_analysis_view(request, flock_id):
    """
    API view for detailed production analysis of a specific flock
    """
    try:
        user = request.user
        
        if user.role in ['admin']:
            from apps.birds.models.models import Flock
            flock = Flock.objects.get(id=flock_id)
        else:
            from apps.birds.models.models import Flock
            flock = Flock.objects.get(
                Q(farm__owner=user) | 
                Q(farm__managers=user) |
                Q(created_by=user),
                id=flock_id
            )
        
        # Feed consumption analysis
        feed_records = flock.feed_records.all().order_by('date')
        total_feed_consumed = feed_records.aggregate(total=Sum('quantity_kg'))['total'] or 0
        total_feed_cost = sum(record.total_cost for record in feed_records)
        
        # Egg production analysis (if applicable)
        egg_data = {}
        if flock.flock_type in ['layer', 'breeder']:
            egg_records = flock.egg_productions.all().order_by('date')
            total_eggs = egg_records.aggregate(total=Sum('total_eggs'))['total'] or 0
            avg_production_rate = egg_records.aggregate(avg=Avg('production_rate'))['avg'] or 0
            
            egg_data = {
                'total_eggs_produced': total_eggs,
                'average_production_rate': avg_production_rate,
                'production_trend': [
                    {
                        'date': record.date,
                        'total_eggs': record.total_eggs,
                        'production_rate': record.production_rate
                    }
                    for record in egg_records[-30:]  # Last 30 records
                ]
            }
        
        # Weight tracking analysis
        weight_records = flock.weight_records.all().order_by('date')
        weight_trend = [
            {
                'date': record.date,
                'average_weight': record.average_weight,
                'age_in_days': record.age_in_days
            }
            for record in weight_records
        ]
        
        # Feed conversion ratio (if weight data available)
        fcr = None
        if weight_records.exists() and total_feed_consumed > 0:
            latest_weight = weight_records.last()
            if latest_weight:
                weight_gain = latest_weight.average_weight - (weight_records.first().average_weight if weight_records.first() else 0)
                if weight_gain > 0:
                    fcr = total_feed_consumed / (weight_gain * flock.current_count / 1000)  # Convert to kg
        
        analysis_data = {
            'flock_info': {
                'id': flock.id,
                'flock_id': flock.flock_id,
                'breed': flock.breed.name,
                'flock_type': flock.flock_type,
                'current_count': flock.current_count,
                'age_in_days': flock.age_in_days
            },
            'feed_analysis': {
                'total_consumed_kg': total_feed_consumed,
                'total_cost': total_feed_cost,
                'feed_per_bird': total_feed_consumed / flock.current_count if flock.current_count > 0 else 0,
                'cost_per_bird': total_feed_cost / flock.current_count if flock.current_count > 0 else 0,
                'feed_conversion_ratio': fcr
            },
            'egg_production': egg_data,
            'weight_tracking': {
                'records_count': weight_records.count(),
                'weight_trend': weight_trend,
                'current_average_weight': weight_records.last().average_weight if weight_records.exists() else None
            },
            'performance_indicators': {
                'survival_rate': (flock.current_count / flock.initial_count * 100) if flock.initial_count > 0 else 0,
                'days_in_production': flock.age_in_days,
                'feed_efficiency': fcr
            }
        }
        
        return Response(analysis_data)
        
    except:
        from apps.birds.models.models import Flock
        return Response({'error': 'Flock not found'}, status=status.HTTP_404_NOT_FOUND)
