from django.db import models
from django.contrib.auth import get_user_model

"""Broiler-focused bird models (farms/buildings removed)."""

User = get_user_model()


class Batch(models.Model):
    """
    Model representing different batches of broilers
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("sold", "Sold"),
    ]
    batch_number = models.CharField(max_length=100, unique=True)
    supplier = models.CharField(max_length=100)
    collection_date = models.DateTimeField(auto_now_add=True)
    initial_count = models.PositiveIntegerField()
    current_count = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_batch"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "batches"
        verbose_name = "batch"
        verbose_name_plural = "batches"
        ordering = ["-created_at"]

    def __str__(self):
        return self.batch_number

    @property
    def age_in_days(self):
        from django.utils import timezone
        import datetime

        return (datetime.datetime.today() - self.collection_date).days

    @property
    def mortality_rate(self):
        if self.initial_count == 0:
            return 0
        return (
            ((self.initial_count - self.current_count) / self.initial_count) * 100
            if self.initial_count and self.current_count
            else None
        )
