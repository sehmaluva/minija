from django.db import models


class Sale(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"Sale {self.date} ({self.quantity})"


class Cost(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Cost {self.date} - {self.amount}"


class Transaction(models.Model):
    date = models.DateField()
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Transaction {self.date} - {self.amount}"
