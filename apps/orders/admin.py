from django.contrib import admin
from .models import ChickOrder, Reminder


@admin.register(ChickOrder)
class ChickOrderAdmin(admin.ModelAdmin):
    list_display = ('date', 'quantity', 'supplier', 'received')


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('date', 'title', 'completed')
