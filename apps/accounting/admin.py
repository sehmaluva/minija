from django.contrib import admin
from .models.models import Sale, Cost, Transaction


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "organization",
        "description",
        "quantity",
        "unit_price",
        "total",
    )
    list_filter = ("organization",)


@admin.register(Cost)
class CostAdmin(admin.ModelAdmin):
    list_display = ("date", "organization", "description", "amount")
    list_filter = ("organization",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "organization", "source", "amount")
    list_filter = ("organization",)
