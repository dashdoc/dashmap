from django.db import models
from django.contrib.auth.models import User
from vehicles.models import Vehicle

class Stop(models.Model):
    STOP_TYPES = [
        ('loading', 'Loading'),
        ('unloading', 'Unloading'),
    ]

    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    stop_type = models.CharField(max_length=10, choices=STOP_TYPES)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.stop_type})"

class Trip(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    dispatcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispatched_trips')
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    planned_start_date = models.DateField()
    planned_start_time = models.TimeField()
    actual_start_datetime = models.DateTimeField(null=True, blank=True)
    actual_end_datetime = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    driver_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.vehicle.license_plate}"

class TripStop(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_stops')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='trip_stops')
    order = models.PositiveIntegerField()
    planned_arrival_time = models.TimeField()
    actual_arrival_datetime = models.DateTimeField(null=True, blank=True)
    actual_departure_datetime = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        unique_together = ['trip', 'order']

    def __str__(self):
        return f"{self.trip.name} - Stop {self.order}: {self.stop.name}"
