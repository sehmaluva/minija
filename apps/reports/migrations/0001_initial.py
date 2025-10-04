"""Initial migration for reports app after farm removal."""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('birds', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('report_type', models.CharField(choices=[('production', 'Production Report'), ('health', 'Health Report'), ('financial', 'Financial Report'), ('mortality', 'Mortality Report'), ('feed_consumption', 'Feed Consumption Report'), ('custom', 'Custom Report')], max_length=20)),
                ('report_format', models.CharField(choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')], max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('file_path', models.FileField(blank=True, null=True, upload_to='reports/')),
                ('parameters', models.JSONField(blank=True, default=dict)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('flocks', models.ManyToManyField(blank=True, to='birds.flock')),
                ('generated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generated_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
                'db_table': 'reports',
                'ordering': ['-generated_at'],
            },
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_type', models.CharField(choices=[('mortality_high', 'High Mortality Rate'), ('production_low', 'Low Production'), ('feed_low', 'Low Feed Stock'), ('vaccination_due', 'Vaccination Due'), ('medication_due', 'Medication Due'), ('environmental', 'Environmental Alert'), ('system', 'System Alert')], max_length=20)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], max_length=10)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_alerts', to=settings.AUTH_USER_MODEL)),
                ('flock', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='birds.flock')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resolved_alerts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Alert',
                'verbose_name_plural': 'Alerts',
                'db_table': 'alerts',
                'ordering': ['-created_at'],
            },
        ),
    ]
