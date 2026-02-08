from django.contrib import admin
from .models import ChickOrder, Reminder


@admin.register(ChickOrder)
class ChickOrderAdmin(admin.ModelAdmin):
    list_display = ("date", "organization", "quantity", "supplier", "received")
    list_filter = ("organization",)


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("date", "organization", "title", "completed")
    list_filter = ("organization",)
