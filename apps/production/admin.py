from django.contrib import admin
from apps.production.models.models import FeedRecord, EggProduction, WeightRecord, EnvironmentalRecord


@admin.register(FeedRecord)
class FeedRecordAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'feed_type', 'quantity_kg', 'cost_per_kg', 'total_cost', 'recorded_by')
    list_filter = ('feed_type', 'date', 'brand')
    search_fields = ('batch__batch_number', 'brand', 'supplier')
    readonly_fields = ('total_cost', 'created_at')

@admin.register(EggProduction)
class EggProductionAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'total_eggs', 'production_rate', 'average_weight', 'recorded_by')
    list_filter = ('date', 'flock__flock_type')
    search_fields = ('batch__batch_id',)
    readonly_fields = ('production_rate', 'created_at')

@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'sample_size', 'average_weight', 'age_in_days', 'recorded_by')
    list_filter = ('date',)
    search_fields = ('batch__batch_number',)
    readonly_fields = ('created_at',)

@admin.register(EnvironmentalRecord)
class EnvironmentalRecordAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'temperature', 'humidity', 'ammonia_level', 'recorded_by')
    list_filter = ('date',)
    search_fields = ('batch__batch_number',)
    readonly_fields = ('created_at',)
