"""_summary_
Serializers for accounting models.
"""

from rest_framework import serializers  # type: ignore[reportMissingTypeStubs]
from apps.accounting.models.models import Sale, Cost, Transaction


class SaleSerializer(serializers.ModelSerializer):
    """Serializer for Sale model."""

    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        """Meta class for SaleSerializer."""

        model = Sale
        fields = ["id", "date", "description", "quantity", "unit_price", "total"]


class CostSerializer(serializers.ModelSerializer):
    """Serializer for Cost model."""

    class Meta:
        """Meta class for CostSerializer."""

        model = Cost
        fields = ["id", "date", "description", "amount"]


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""

    class Meta:
        """Meta class for TransactionSerializer."""

        model = Transaction
        fields = ["id", "date", "source", "amount", "note"]
