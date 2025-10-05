from django.contrib import admin
from apps.birds.models.models import Breed, Flock, FlockMovement, Batch

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

