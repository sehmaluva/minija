from django.contrib import admin
from apps.farms.models.models import Farm, Building

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'owner', 'license_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'state', 'country', 'created_at')
    search_fields = ('name', 'city', 'license_number', 'owner__email')
    filter_horizontal = ('managers',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'license_number', 'established_date')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Management', {
            'fields': ('owner', 'managers', 'total_area', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'building_type', 'capacity', 'area', 'is_active', 'construction_date')
    list_filter = ('building_type', 'is_active', 'farm', 'construction_date')
    search_fields = ('name', 'farm__name')
    readonly_fields = ('created_at', 'updated_at', 'area')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'name', 'building_type', 'capacity')
        }),
        ('Dimensions', {
            'fields': ('length', 'width', 'height', 'area')
        }),
        ('Additional Information', {
            'fields': ('construction_date', 'is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
