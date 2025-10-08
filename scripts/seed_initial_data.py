"""
Script to seed initial data for the poultry management system
Run this after creating the database tables
"""

import os
import sys
import django
from django.contrib.auth import get_user_model

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


User = get_user_model()


def create_initial_data():
    """Create initial data for the poultry management system."""
    print("Creating initial data for poultry management system...")

    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email="admin@poultry.com",
        defaults={
            "username": "admin",
            "first_name": "System",
            "last_name": "Administrator",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin_user.set_password("admin123")
        admin_user.save()
        print("✓ Created admin user")

    # Create standard user
    standard_user, created = User.objects.get_or_create(
        email="user@poultry.com",
        defaults={
            "username": "standarduser",
            "first_name": "Standard",
            "last_name": "User",
            "role": "user",
        },
    )
    if created:
        standard_user.set_password("user123")
        standard_user.save()
        print("✓ Created standard user")

    print("\n Initial data creation completed successfully!")
    print("\nDefault login credentials:")
    print("Admin: admin@poultry.com / admin123")
    print("Standard User: user@poultry.com / user123")


if __name__ == "__main__":
    create_initial_data()
