"""
Script to seed initial data for the poultry management system
Run this after creating the database tables
"""

import os
import sys
import django
from datetime import date, datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
# from apps.users.models.models import User
from apps.farms.models.models import Farm, Building
from apps.birds.models.models import Breed, Flock
from apps.health.models.models import HealthRecord, Vaccination
from apps.production.models.models import FeedRecord, EggProduction

User = get_user_model()

def create_initial_data():
    print("Creating initial data for poultry management system...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@poultry.com',
        defaults={
            'username': 'admin',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Created admin user")
    
    # Create farm manager
    manager_user, created = User.objects.get_or_create(
        email='manager@poultry.com',
        defaults={
            'username': 'manager',
            'first_name': 'Farm',
            'last_name': 'Manager',
            'role': 'manager'
        }
    )
    if created:
        manager_user.set_password('manager123')
        manager_user.save()
        print("✓ Created manager user")
    
    # Create veterinarian
    vet_user, created = User.objects.get_or_create(
        email='vet@poultry.com',
        defaults={
            'username': 'veterinarian',
            'first_name': 'Dr. John',
            'last_name': 'Smith',
            'role': 'veterinarian'
        }
    )
    if created:
        vet_user.set_password('vet123')
        vet_user.save()
        print("✓ Created veterinarian user")
    
    # Create breeds
    breeds_data = [
        {
            'name': 'Rhode Island Red',
            'species': 'Chicken',
            'description': 'Hardy dual-purpose breed known for good egg production',
            'average_weight': 2.5,
            'egg_production_rate': 250,
            'maturity_age': 150
        },
        {
            'name': 'Leghorn',
            'species': 'Chicken', 
            'description': 'Excellent white egg layer breed',
            'average_weight': 2.0,
            'egg_production_rate': 300,
            'maturity_age': 140
        },
        {
            'name': 'Broiler Ross 308',
            'species': 'Chicken',
            'description': 'Fast-growing meat production breed',
            'average_weight': 2.8,
            'egg_production_rate': 0,
            'maturity_age': 42
        },
        {
            'name': 'ISA Brown',
            'species': 'Chicken',
            'description': 'Commercial brown egg layer hybrid',
            'average_weight': 2.2,
            'egg_production_rate': 320,
            'maturity_age': 145
        }
    ]
    
    for breed_data in breeds_data:
        breed, created = Breed.objects.get_or_create(
            name=breed_data['name'],
            defaults=breed_data
        )
        if created:
            print(f"✓ Created breed: {breed.name}")
    
    # Create sample farm
    farm, created = Farm.objects.get_or_create(
        name='Sunrise Poultry Farm',
        defaults={
            'description': 'A modern commercial poultry operation',
            'address': '123 Farm Road',
            'city': 'Farmville',
            'state': 'Iowa',
            'country': 'USA',
            'postal_code': '12345',
            'phone_number': '+1-555-0123',
            'email': 'info@sunrisepoultry.com',
            'license_number': 'PF-2024-001',
            'established_date': date(2020, 1, 15),
            'total_area': 50.0,
            'owner': admin_user
        }
    )
    if created:
        farm.managers.add(manager_user)
        print(f"✓ Created farm: {farm.name}")
    
    # Create buildings
    buildings_data = [
        {
            'name': 'Layer House 1',
            'building_type': 'layer_house',
            'capacity': 5000,
            'length': 100.0,
            'width': 15.0,
            'height': 4.0,
            'construction_date': date(2020, 3, 1)
        },
        {
            'name': 'Broiler House 1',
            'building_type': 'broiler_house',
            'capacity': 10000,
            'length': 120.0,
            'width': 18.0,
            'height': 4.5,
            'construction_date': date(2020, 4, 15)
        },
        {
            'name': 'Feed Storage',
            'building_type': 'feed_storage',
            'capacity': 0,
            'length': 30.0,
            'width': 20.0,
            'height': 8.0,
            'construction_date': date(2020, 2, 1)
        }
    ]
    
    for building_data in buildings_data:
        building, created = Building.objects.get_or_create(
            farm=farm,
            name=building_data['name'],
            defaults=building_data
        )
        if created:
            print(f"✓ Created building: {building.name}")
    
    # Create sample flocks
    layer_house = Building.objects.get(farm=farm, name='Layer House 1')
    broiler_house = Building.objects.get(farm=farm, name='Broiler House 1')
    
    leghorn_breed = Breed.objects.get(name='Leghorn')
    broiler_breed = Breed.objects.get(name='Broiler Ross 308')
    
    # Layer flock
    layer_flock, created = Flock.objects.get_or_create(
        flock_id='LH1-2024-001',
        defaults={
            'farm': farm,
            'building': layer_house,
            'breed': leghorn_breed,
            'flock_type': 'layer',
            'initial_count': 4500,
            'current_count': 4350,
            'hatch_date': date.today() - timedelta(days=180),
            'source': 'Premium Hatchery Inc.',
            'status': 'active',
            'notes': 'High-performing layer flock',
            'created_by': manager_user
        }
    )
    if created:
        print(f"✓ Created flock: {layer_flock.flock_id}")
    
    # Broiler flock
    broiler_flock, created = Flock.objects.get_or_create(
        flock_id='BH1-2024-001',
        defaults={
            'farm': farm,
            'building': broiler_house,
            'breed': broiler_breed,
            'flock_type': 'broiler',
            'initial_count': 9500,
            'current_count': 9200,
            'hatch_date': date.today() - timedelta(days=35),
            'source': 'Commercial Hatchery Ltd.',
            'status': 'active',
            'notes': 'Fast-growing broiler batch',
            'created_by': manager_user
        }
    )
    if created:
        print(f"✓ Created flock: {broiler_flock.flock_id}")
    
    # Create sample health records
    vaccination, created = HealthRecord.objects.get_or_create(
        flock=layer_flock,
        record_type='vaccination',
        date=datetime.now() - timedelta(days=30),
        defaults={
            'description': 'Newcastle Disease vaccination',
            'veterinarian': vet_user,
            'cost': 450.00,
            'notes': 'Routine vaccination program',
            'created_by': vet_user
        }
    )
    if created:
        Vaccination.objects.create(
            health_record=vaccination,
            vaccine_name='Newcastle Disease Vaccine',
            manufacturer='VetPharma Inc.',
            batch_number='ND-2024-045',
            dosage='0.5ml per bird',
            administration_method='Drinking water',
            birds_vaccinated=4350,
            next_vaccination_date=date.today() + timedelta(days=90)
        )
        print("✓ Created vaccination record")
    
    # Create sample feed records
    feed_record, created = FeedRecord.objects.get_or_create(
        flock=layer_flock,
        date=date.today() - timedelta(days=1),
        defaults={
            'feed_type': 'layer',
            'brand': 'Premium Layer Feed',
            'quantity_kg': 500.0,
            'cost_per_kg': 0.85,
            'supplier': 'Farm Supply Co.',
            'batch_number': 'LF-2024-156',
            'recorded_by': manager_user
        }
    )
    if created:
        print("✓ Created feed record")
    
    # Create sample egg production record
    egg_production, created = EggProduction.objects.get_or_create(
        flock=layer_flock,
        date=date.today() - timedelta(days=1),
        defaults={
            'total_eggs': 3800,
            'grade_a_eggs': 3200,
            'grade_b_eggs': 450,
            'grade_c_eggs': 100,
            'cracked_eggs': 35,
            'dirty_eggs': 15,
            'average_weight': 62.5,
            'recorded_by': manager_user
        }
    )
    if created:
        print("✓ Created egg production record")
    
    print("\n🎉 Initial data creation completed successfully!")
    print("\nDefault login credentials:")
    print("Admin: admin@poultry.com / admin123")
    print("Manager: manager@poultry.com / manager123") 
    print("Veterinarian: vet@poultry.com / vet123")

if __name__ == '__main__':
    create_initial_data()
