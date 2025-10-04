"""Initial migration for birds app after farm removal."""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Breed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('species', models.CharField(default='Chicken', max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('average_weight', models.DecimalField(decimal_places=2, help_text='Average weight in kg', max_digits=6)),
                ('egg_production_rate', models.DecimalField(blank=True, decimal_places=2, help_text='Eggs per year', max_digits=5, null=True)),
                ('maturity_age', models.PositiveIntegerField(help_text='Maturity age in days')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Breed',
                'verbose_name_plural': 'Breeds',
                'db_table': 'breeds',
            },
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_number', models.CharField(max_length=100, unique=True)),
                ('supplier', models.CharField(max_length=100)),
                ('collection_date', models.DateTimeField(auto_now_add=True)),
                ('initial_count', models.PositiveIntegerField()),
                ('current_count', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('sold', 'Sold')], default='active', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_batch', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'batch',
                'verbose_name_plural': 'batches',
                'db_table': 'batches',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Flock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, help_text='Optional location / house tag', max_length=120, null=True)),
                ('flock_id', models.CharField(max_length=50, unique=True)),
                ('flock_type', models.CharField(choices=[('broiler', 'Broiler'), ('layer', 'Layer'), ('breeder', 'Breeder'), ('pullet', 'Pullet')], max_length=20)),
                ('initial_count', models.PositiveIntegerField()),
                ('current_count', models.PositiveIntegerField()),
                ('hatch_date', models.DateField()),
                ('source', models.CharField(help_text='Hatchery or supplier', max_length=200)),
                ('status', models.CharField(choices=[('active', 'Active'), ('sold', 'Sold'), ('processed', 'Processed'), ('deceased', 'Deceased'), ('transferred', 'Transferred')], default='active', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('breed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flocks', to='birds.breed')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_flocks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Flock',
                'verbose_name_plural': 'Flocks',
                'db_table': 'flocks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FlockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_type', models.CharField(choices=[('transfer', 'Transfer'), ('sale', 'Sale'), ('processing', 'Processing'), ('mortality', 'Mortality'), ('culling', 'Culling')], max_length=20)),
                ('from_location', models.CharField(blank=True, max_length=120, null=True)),
                ('to_location', models.CharField(blank=True, max_length=120, null=True)),
                ('bird_count', models.PositiveIntegerField()),
                ('movement_date', models.DateTimeField()),
                ('reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('flock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movements', to='birds.flock')),
                ('recorded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recorded_movements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Flock Movement',
                'verbose_name_plural': 'Flock Movements',
                'db_table': 'flock_movements',
                'ordering': ['-movement_date'],
            },
        ),
    ]
