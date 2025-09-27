from django.db import models
from django.utils import timezone


class HistoricalEntry(models.Model):
	"""Lightweight model to store past daily metrics used for simple forecasting.

	Fields:
	- date: date of the record
	- feed_kg: kilograms of feed used that day
	- birds_count: number of birds present (optional)
	- note: optional note
	"""
	date = models.DateField(default=timezone.now)
	feed_kg = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
	birds_count = models.IntegerField(null=True, blank=True)
	note = models.CharField(max_length=255, blank=True)

	class Meta:
		ordering = ['-date']

	def __str__(self):
		return f"HistoricalEntry {self.date} - {self.feed_kg}kg"
