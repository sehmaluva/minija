from rest_framework import serializers
from apps.orders.models import ChickOrder, Reminder


class ChickOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChickOrder
        fields = ["id", "date", "quantity", "supplier", "received", "notes"]


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ["id", "date", "title", "message", "completed"]
