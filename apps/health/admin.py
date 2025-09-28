from django.contrib import admin
from apps.health.models.models import HealthRecord, Vaccination, Medication, MortalityRecord

class VaccinationInline(admin.StackedInline):
    model = Vaccination
    extra = 0

class MedicationInline(admin.StackedInline):
    model = Medication
    extra = 0

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('batch', 'record_type', 'date', 'veterinarian', 'cost', 'created_by', 'created_at')
    list_filter = ('record_type', 'date', 'veterinarian', 'created_at')
    search_fields = ('flock__flock_id', 'description')
    inlines = [VaccinationInline, MedicationInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MortalityRecord)
class MortalityRecordAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'count', 'cause_category', 'age_at_death', 'recorded_by', 'created_at')
    list_filter = ('cause_category', 'date', 'created_at')
    search_fields = ('flock__flock_id', 'specific_cause')
    readonly_fields = ('created_at',)
