from django.contrib import admin
from apps.flocks.models.models import Breed, Flock, FlockMovement, Batch

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'supplier', 'collection_date', 'initial_count', 'current_count', 'created_by')
    list_filter = ('supplier', 'created_at')
    search_fields = ('batch_number',)
    readonly_fields = ('created_at','collection_date', 'updated_at', 'age_in_days', 'mortality_rate')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('batch_number', )
        }),
        ('Flock Details', {
            'fields': ('initial_count', 'current_count', 'collection_date', 'supplier')
        }),
        ('Management', {
            'fields': ('created_by', 'notes')
        }),
        ('Calculated Fields', {
            'fields': ('age_in_days', 'mortality_rate'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'average_weight', 'egg_production_rate', 'maturity_age', 'created_at')
    list_filter = ('species', 'created_at')
    search_fields = ('name', 'species')
    readonly_fields = ('created_at',)

@admin.register(Flock)
class FlockAdmin(admin.ModelAdmin):
    list_display = ('flock_id', 'farm', 'breed', 'flock_type', 'current_count', 'status', 'age_in_days', 'created_at')
    list_filter = ('flock_type', 'status', 'farm', 'breed', 'created_at')
    search_fields = ('flock_id', 'farm__name', 'breed__name')
    readonly_fields = ('created_at', 'updated_at', 'age_in_days', 'mortality_rate')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'building', 'breed', 'flock_id', 'flock_type')
        }),
        ('Flock Details', {
            'fields': ('initial_count', 'current_count', 'hatch_date', 'source', 'status')
        }),
        ('Management', {
            'fields': ('created_by', 'notes')
        }),
        ('Calculated Fields', {
            'fields': ('age_in_days', 'mortality_rate'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(FlockMovement)
class FlockMovementAdmin(admin.ModelAdmin):
    list_display = ('flock', 'movement_type', 'bird_count', 'movement_date', 'recorded_by', 'created_at')
    list_filter = ('movement_type', 'movement_date', 'created_at')
    search_fields = ('flock__flock_id', 'reason')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('flock', 'movement_type', 'bird_count', 'movement_date')
        }),
        ('Location', {
            'fields': ('from_building', 'to_building')
        }),
        ('Details', {
            'fields': ('reason', 'recorded_by')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
