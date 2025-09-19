from django.contrib import admin
from .models import Sale, Cost, Transaction


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'quantity', 'unit_price', 'total')


@admin.register(Cost)
class CostAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'source', 'amount')
