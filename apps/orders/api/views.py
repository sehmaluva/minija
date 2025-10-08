from rest_framework import viewsets
from apps.orders.models import ChickOrder, Reminder
from .serializers import ChickOrderSerializer, ReminderSerializer


class ChickOrderViewSet(viewsets.ModelViewSet):
    queryset = ChickOrder.objects.all().order_by("-date")
    serializer_class = ChickOrderSerializer


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all().order_by("-date")
    serializer_class = ReminderSerializer
