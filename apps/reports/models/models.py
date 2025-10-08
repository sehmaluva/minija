from django.db import models
from django.contrib.auth import get_user_model
from apps.birds.models.models import Batch

User = get_user_model()

class Report(models.Model):
    """
    Model for storing generated reports
    """
    REPORT_TYPES = [
        ('production', 'Production Report'),
        ('health', 'Health Report'),
        ('financial', 'Financial Report'),
        ('mortality', 'Mortality Report'),
        ('feed_consumption', 'Feed Consumption Report'),
        ('custom', 'Custom Report'),
    ]

    REPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]

    # Removed farm foreign key in simplified multi-tenant model
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    report_format = models.CharField(max_length=10, choices=REPORT_FORMATS)
    start_date = models.DateField()
    end_date = models.DateField()
    batches = models.ManyToManyField(Batch, blank=True)
    file_path = models.FileField(upload_to='reports/', null=True, blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%Y-%m-%d')}"

class Alert(models.Model):
    """
    Model for system alerts and notifications
    """
    ALERT_TYPES = [
        ('mortality_high', 'High Mortality Rate'),
        ('production_low', 'Low Production'),
        ('feed_low', 'Low Feed Stock'),
        ('vaccination_due', 'Vaccination Due'),
        ('medication_due', 'Medication Due'),
        ('environmental', 'Environmental Alert'),
        ('system', 'System Alert'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    # Removed farm foreign key; optional batch reference retained
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resolved_alerts', null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alerts'
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.severity}"
