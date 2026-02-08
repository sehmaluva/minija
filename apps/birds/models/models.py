"""Broiler-focused bird models (farms/buildings removed)."""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Batch(models.Model):
    """
    Model representing different batches of broilers
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("sold", "Sold"),
    ]
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="batches",
        null=True,
        blank=True,
    )
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
        indexes = [
            models.Index(fields=["organization", "status"]),
        ]

    def __str__(self):
        return self.batch_number

    @property
    def age_in_days(self):
        from django.utils import timezone

        # collection_date may be None (partial records) or naive/aware.
        # Return 0 when missing and handle naive/aware datetimes safely.
        if not self.collection_date:
            return 0

        now = timezone.now()
        collection_date = self.collection_date

        try:
            if collection_date.tzinfo is None and timezone.is_aware(now):
                from django.utils import timezone as _tz

                collection_date = _tz.make_aware(collection_date)
        except Exception:
            # Fall back if conversion fails
            pass

        delta = now - collection_date
        return delta.days if hasattr(delta, "days") else 0

    @property
    def mortality_rate(self):
        if self.initial_count == 0:
            return 0
        return (
            ((self.initial_count - self.current_count) / self.initial_count) * 100
            if self.initial_count and self.current_count
            else None
        )
