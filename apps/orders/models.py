from django.db import models


class ChickOrder(models.Model):
    date = models.DateField()
    quantity = models.IntegerField()
    supplier = models.CharField(max_length=200, blank=True)
    received = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"ChickOrder {self.date} ({self.quantity})"


class Reminder(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder {self.date} - {self.title}"
