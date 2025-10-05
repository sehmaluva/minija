from django.db import models
from django.contrib.auth import get_user_model
from apps.birds.models.models import Batch
from decimal import Decimal

User = get_user_model()

class FeedRecord(models.Model):
    """
    Model for tracking feed consumption
    """
    FEED_TYPES = [
        ('starter', 'Starter Feed'),
        ('grower', 'Grower Feed'),
        ('finisher', 'Finisher Feed'),
        ('mash', 'Mixed Mash Maize Crumbs'),
    ]
    
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='feed_records')
    date = models.DateField()
    feed_type = models.CharField(max_length=20, choices=FEED_TYPES)
    brand = models.CharField(max_length=200)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    supplier = models.CharField(max_length=200)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_feeds')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feed_records'
        verbose_name = 'Feed Record'
        verbose_name_plural = 'Feed Records'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.batch.batch_number} - {self.feed_type} - {self.quantity_kg}kg"
    
    @property
    def total_cost(self):
        if self.quantity_kg is not None and self.cost_per_kg is not None:
            return self.quantity_kg * self.cost_per_kg
        return Decimal('0.00')
         
class EggProduction(models.Model):
    """
    Model for tracking egg production (for layers and breeders)
    """
    EGG_GRADES = [
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B'),
        ('grade_c', 'Grade C'),
        ('cracked', 'Cracked'),
        ('dirty', 'Dirty'),
    ]
    
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='egg_productions')
    date = models.DateField()
    total_eggs = models.PositiveIntegerField()
    grade_a_eggs = models.PositiveIntegerField(default=0)
    grade_b_eggs = models.PositiveIntegerField(default=0)
    grade_c_eggs = models.PositiveIntegerField(default=0)
    cracked_eggs = models.PositiveIntegerField(default=0)
    dirty_eggs = models.PositiveIntegerField(default=0)
    average_weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Average egg weight in grams")
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_egg_productions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'egg_productions'
        verbose_name = 'Egg Production'
        verbose_name_plural = 'Egg Productions'
        ordering = ['-date']
        unique_together = ['batch', 'date']
    
    def __str__(self):
        return f"{self.batch.batch_id} - {self.date} - {self.total_eggs} eggs"
    
    @property
    def production_rate(self):
        if self.batch.current_count == 0:
            return 0
        return (self.total_eggs / self.batch.current_count) * 100

class WeightRecord(models.Model):
    """
    Model for tracking bird weight measurements
    """
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='weight_records')
    date = models.DateField()
    sample_size = models.PositiveIntegerField(help_text="Number of birds weighed")
    average_weight = models.DecimalField(max_digits=6, decimal_places=2, help_text="Average weight in grams")
    min_weight = models.DecimalField(max_digits=6, decimal_places=2, help_text="Minimum weight in grams")
    max_weight = models.DecimalField(max_digits=6, decimal_places=2, help_text="Maximum weight in grams")
    age_in_days = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_weights')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'weight_records'
        verbose_name = 'Weight Record'
        verbose_name_plural = 'Weight Records'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.batch.batch_number} - {self.date} - {self.average_weight}g avg"

class EnvironmentalRecord(models.Model):
    """
    Model for tracking environmental conditions
    """
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='environmental_records')
    date = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temperature in Celsius")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, help_text="Humidity percentage")
    ammonia_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Ammonia level in ppm")
    ventilation_rate = models.CharField(max_length=100, blank=True, null=True)
    lighting_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_environmental')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'environmental_records'
        verbose_name = 'Environmental Record'
        verbose_name_plural = 'Environmental Records'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.batch.batch_number} - {self.date.strftime('%Y-%m-%d %H:%M')} - {self.temperature}°C"
