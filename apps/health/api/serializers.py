from rest_framework import serializers
from apps.health.models.models import HealthRecord, Vaccination, Medication, MortalityRecord
from apps.birds.api.serializers import FlockSerializer
from apps.users.api.serializers import UserSerializer

class VaccinationSerializer(serializers.ModelSerializer):
    """
    Serializer for Vaccination model
    """
    class Meta:
        model = Vaccination
        fields = [
            'vaccine_name', 'manufacturer', 'batch_number', 'dosage',
            'administration_method', 'birds_vaccinated', 'next_vaccination_date'
        ]

class MedicationSerializer(serializers.ModelSerializer):
    """
    Serializer for Medication model
    """
    class Meta:
        model = Medication
        fields = [
            'medication_name', 'manufacturer', 'dosage', 'administration_method',
            'duration_days', 'withdrawal_period', 'birds_treated'
        ]

class HealthRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for HealthRecord model
    """
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True)
    veterinarian_name = serializers.CharField(source='veterinarian.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    vaccination_details = VaccinationSerializer(read_only=True)
    medication_details = MedicationSerializer(read_only=True)

    class Meta:
        model = HealthRecord
        fields = [
            'id', 'batch', 'batch_id', 'record_type', 'date', 'description',
            'veterinarian', 'veterinarian_name', 'cost', 'notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'vaccination_details', 'medication_details'
        ]
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class HealthRecordCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating health records with nested details
    """
    vaccination_details = VaccinationSerializer(required=False)
    medication_details = MedicationSerializer(required=False)

    class Meta:
        model = HealthRecord
        fields = [
            'batch', 'record_type', 'date', 'description', 'veterinarian',
            'cost', 'notes', 'vaccination_details', 'medication_details'
        ]

    def create(self, validated_data):
        vaccination_data = validated_data.pop('vaccination_details', None)
        medication_data = validated_data.pop('medication_details', None)

        validated_data['created_by'] = self.context['request'].user
        health_record = HealthRecord.objects.create(**validated_data)

        if vaccination_data and health_record.record_type == 'vaccination':
            Vaccination.objects.create(health_record=health_record, **vaccination_data)

        if medication_data and health_record.record_type == 'medication':
            Medication.objects.create(health_record=health_record, **medication_data)

        return health_record

class MortalityRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for MortalityRecord model
    """
    batch_id = serializers.CharField(source='batch.batch_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)

    class Meta:
        model = MortalityRecord
        fields = [
            'id', 'batch', 'batch_id', 'date', 'count', 'cause_category',
            'specific_cause', 'age_at_death', 'notes', 'recorded_by',
            'recorded_by_name', 'created_at'
        ]
        read_only_fields = ('id', 'recorded_by', 'created_at')

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        mortality_record = super().create(validated_data)

        # Update batch current count
        batch = mortality_record.batch
        batch.current_count = max(0, batch.current_count - mortality_record.count)
        if batch.current_count == 0:
            batch.status = 'deceased'
        batch.save()

        return mortality_record
