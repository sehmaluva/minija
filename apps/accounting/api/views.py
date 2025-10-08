from rest_framework import viewsets
from apps.accounting.models.models import Sale, Cost, Transaction
from .serializers import SaleSerializer, CostSerializer, TransactionSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by("-date")
    serializer_class = SaleSerializer


class CostViewSet(viewsets.ModelViewSet):
    queryset = Cost.objects.all().order_by("-date")
    serializer_class = CostSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by("-date")
    serializer_class = TransactionSerializer
