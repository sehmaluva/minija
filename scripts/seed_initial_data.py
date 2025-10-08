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

    # Create standard user
    standard_user, created = User.objects.get_or_create(
        email='user@poultry.com',
        defaults={
            'username': 'standarduser',
            'first_name': 'Standard',
            'last_name': 'User',
            'role': 'user'
        }
    )
    if created:
        standard_user.set_password('user123')
        standard_user.save()
        print("✓ Created standard user")

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

    # Create sample locations (simple strings now)
    layer_location = 'Layer House 1'
    broiler_location = 'Broiler House 1'

    leghorn_breed = Breed.objects.get(name='Leghorn')
    broiler_breed = Breed.objects.get(name='Broiler Ross 308')

    # Layer flock
    layer_flock, created = Flock.objects.get_or_create(
        flock_id='LH1-2024-001',
        defaults={
            'breed': leghorn_breed,
            'flock_type': 'layer',
            'initial_count': 4500,
            'current_count': 4350,
            'hatch_date': date.today() - timedelta(days=180),
            'source': 'Premium Hatchery Inc.',
            'status': 'active',
            'location': layer_location,
            'notes': 'High-performing layer flock',
            'created_by': standard_user
        }
    )
    if created:
        print(f"✓ Created flock: {layer_flock.flock_id}")

    # Broiler flock
    broiler_flock, created = Flock.objects.get_or_create(
        flock_id='BH1-2024-001',
        defaults={
            'breed': broiler_breed,
            'flock_type': 'broiler',
            'initial_count': 9500,
            'current_count': 9200,
            'hatch_date': date.today() - timedelta(days=35),
            'source': 'Commercial Hatchery Ltd.',
            'status': 'active',
            'location': broiler_location,
            'notes': 'Fast-growing broiler batch',
            'created_by': standard_user
        }
    )
    if created:
        print(f"✓ Created flock: {broiler_flock.flock_id}")

    # Create sample health records
    # (Health records skipped in simplified seed for now)

    # Create sample feed records
    # (Feed and egg production records skipped for simplicity)

    # Create sample egg production record


    print("\n🎉 Initial data creation completed successfully!")
    print("\nDefault login credentials:")
    print("Admin: admin@poultry.com / admin123")
    print("Standard User: user@poultry.com / user123")

if __name__ == '__main__':
    create_initial_data()
