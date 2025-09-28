from django.db import models
from django.contrib.auth import get_user_model
from apps.farms.models.models import Farm, Building

User = get_user_model()

class Batch(models.Model):
    """
    Model representing different batches of broilers
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        
        ]
    batch_number = models.CharField(max_length=100, unique=True)
    supplier = models.CharField(max_length=100)
    collection_date = models.DateTimeField(auto_now_add=True)
    initial_count = models.PositiveIntegerField()
    current_count = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_batch')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'batches'
        verbose_name = 'batch'
        verbose_name_plural = 'batches'
        ordering = ['-created_at']
    
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
        return ((self.initial_count - self.current_count) / self.initial_count) * 100 if self.initial_count and self.current_count else None
    
class Breed(models.Model):
    """
    Model representing different poultry breeds
    """
    name = models.CharField(max_length=100, unique=True)
    species = models.CharField(max_length=50, default='Chicken')
    description = models.TextField(blank=True, null=True)
    average_weight = models.DecimalField(max_digits=6, decimal_places=2, help_text="Average weight in kg")
    egg_production_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Eggs per year")
    maturity_age = models.PositiveIntegerField(help_text="Maturity age in days")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'breeds'
        verbose_name = 'Breed'
        verbose_name_plural = 'Breeds'
    
    def __str__(self):
        return self.name

class Flock(models.Model):
    """
    Model representing a group of birds
    """
    FLOCK_TYPES = [
        ('broiler', 'Broiler'),
        ('layer', 'Layer'),
        ('breeder', 'Breeder'),
        ('pullet', 'Pullet'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('processed', 'Processed'),
        ('deceased', 'Deceased'),
        ('transferred', 'Transferred'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='flocks')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='flocks')
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, related_name='flocks')
    flock_id = models.CharField(max_length=50, unique=True)
    flock_type = models.CharField(max_length=20, choices=FLOCK_TYPES)
    initial_count = models.PositiveIntegerField()
    current_count = models.PositiveIntegerField()
    hatch_date = models.DateField()
    source = models.CharField(max_length=200, help_text="Hatchery or supplier")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_flocks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flocks'
        verbose_name = 'Flock'
        verbose_name_plural = 'Flocks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.flock_id} - {self.breed.name}"
    
    @property
    def age_in_days(self):
        from django.utils import timezone
        return (timezone.now().date() - self.hatch_date).days
    
    @property
    def mortality_rate(self):
        if self.initial_count == 0:
            return 0
        return ((self.initial_count - self.current_count) / self.initial_count) * 100

class FlockMovement(models.Model):
    """
    Model to track flock movements between buildings
    """
    MOVEMENT_TYPES = [
        ('transfer', 'Transfer'),
        ('sale', 'Sale'),
        ('processing', 'Processing'),
        ('mortality', 'Mortality'),
        ('culling', 'Culling'),
    ]
    
    flock = models.ForeignKey(Flock, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    from_building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='outgoing_movements', null=True, blank=True)
    to_building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='incoming_movements', null=True, blank=True)
    bird_count = models.PositiveIntegerField()
    movement_date = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'flock_movements'
        verbose_name = 'Flock Movement'
        verbose_name_plural = 'Flock Movements'
        ordering = ['-movement_date']
    
    def __str__(self):
        return f"{self.flock.flock_id} - {self.movement_type} - {self.bird_count} birds"
