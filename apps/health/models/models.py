from django.db import models
from django.contrib.auth import get_user_model
from apps.birds.models.models import Batch

User = get_user_model()


class HealthRecord(models.Model):
    """
    Model for tracking health records of flocks
    """

    RECORD_TYPES = [
        ("vaccination", "Vaccination"),
        ("medication", "Medication"),
        ("treatment", "Treatment"),
        ("inspection", "Health Inspection"),
        ("disease_outbreak", "Disease Outbreak"),
        ("mortality", "Mortality Record"),
    ]

    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="health_records"
    )
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    date = models.DateTimeField()
    description = models.TextField()
    veterinarian = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="health_records",
        null=True,
        blank=True,
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_health_records"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_records"
        verbose_name = "Health Record"
        verbose_name_plural = "Health Records"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.batch.batch_number} - {self.record_type} - {self.date.strftime('%Y-%m-%d')}"


class Vaccination(models.Model):
    """
    Model for tracking vaccinations
    """

    health_record = models.OneToOneField(
        HealthRecord, on_delete=models.CASCADE, related_name="vaccination_details"
    )
    vaccine_name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200)
    batch_number = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    administration_method = models.CharField(max_length=100)
    birds_vaccinated = models.PositiveIntegerField()
    next_vaccination_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "vaccinations"
        verbose_name = "Vaccination"
        verbose_name_plural = "Vaccinations"

    def __str__(self):
        return f"{self.vaccine_name} - {self.health_record.batch.batch_number}"


class Medication(models.Model):
    """
    Model for tracking medications and treatments
    """

    health_record = models.OneToOneField(
        HealthRecord, on_delete=models.CASCADE, related_name="medication_details"
    )
    medication_name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    administration_method = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField()
    withdrawal_period = models.PositiveIntegerField(
        help_text="Withdrawal period in days"
    )
    birds_treated = models.PositiveIntegerField()

    class Meta:
        db_table = "medications"
        verbose_name = "Medication"
        verbose_name_plural = "Medications"

    def __str__(self):
        return f"{self.medication_name} - {self.health_record. batch.batch_number}"


class MortalityRecord(models.Model):
    """
    Model for tracking bird mortality
    """

    CAUSE_CATEGORIES = [
        ("disease", "Disease"),
        ("accident", "Accident"),
        ("predator", "Predator"),
        ("heat_stress", "Heat Stress"),
        ("cold_stress", "Cold Stress"),
        ("unknown", "Unknown"),
        ("culling", "Culling"),
        ("other", "Other"),
    ]

    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="mortality_records",
        null=True,
        blank=True,
    )
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="mortality_records"
    )
    date = models.DateField()
    count = models.PositiveIntegerField()
    cause_category = models.CharField(max_length=20, choices=CAUSE_CATEGORIES)
    specific_cause = models.CharField(max_length=200, blank=True, null=True)
    age_at_death = models.PositiveIntegerField(help_text="Age in days")
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recorded_mortalities"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mortality_records"
        verbose_name = "Mortality Record"
        verbose_name_plural = "Mortality Records"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.batch.batch_number} - {self.count} birds - {self.date}"
