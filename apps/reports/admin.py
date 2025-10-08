from django.contrib import admin
from apps.reports.models.models import Report, Alert

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'report_format', 'start_date', 'end_date', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'report_format', 'generated_at')
    search_fields = ('title', 'generated_by__email')
    readonly_fields = ('generated_at',)
    filter_horizontal = ('batches',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'severity', 'is_read', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_read', 'is_resolved', 'created_at')
    search_fields = ('title', 'message', 'batch__batch_id')
    readonly_fields = ('created_at', 'resolved_at')

    actions = ['mark_as_read', 'mark_as_resolved']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} alerts marked as read.')

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_by=request.user, resolved_at=timezone.now())
        self.message_user(request, f'{queryset.count()} alerts marked as resolved.')

    mark_as_read.short_description = "Mark selected alerts as read"
    mark_as_resolved.short_description = "Mark selected alerts as resolved"
