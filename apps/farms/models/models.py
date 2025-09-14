from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Farm(models.Model):
    """
    Model representing a poultry farm
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    license_number = models.CharField(max_length=100, unique=True)
    established_date = models.DateField()
    total_area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in acres")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_farms')
    managers = models.ManyToManyField(User, related_name='managed_farms', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farms'
        verbose_name = 'Farm'
        verbose_name_plural = 'Farms'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Building(models.Model):
    """
    Model representing buildings/houses within a farm
    """
    BUILDING_TYPES = [
        ('broiler_house', 'Broiler House'),
        ('layer_house', 'Layer House'),
        ('breeder_house', 'Breeder House'),
        ('nursery', 'Nursery'),
        ('feed_storage', 'Feed Storage'),
        ('equipment_storage', 'Equipment Storage'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField(max_length=100)
    building_type = models.CharField(max_length=20, choices=BUILDING_TYPES)
    capacity = models.PositiveIntegerField(help_text="Maximum number of birds")
    length = models.DecimalField(max_digits=8, decimal_places=2, help_text="Length in meters")
    width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Width in meters")
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Height in meters")
    construction_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'buildings'
        verbose_name = 'Building'
        verbose_name_plural = 'Buildings'
        unique_together = ['farm', 'name']
    
    def __str__(self):
        return f"{self.farm.name} - {self.name}"
    
    @property
    def area(self):
        total = (self.length * self.width)
        return total if total else None
