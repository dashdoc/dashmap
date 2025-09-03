from django.db import models
from vehicles.models import Vehicle

class Position(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='positions')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    speed = models.DecimalField(max_digits=5, decimal_places=2, help_text="Speed in km/h")
    heading = models.DecimalField(max_digits=5, decimal_places=2, help_text="Heading in degrees (0-360)")
    altitude = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Altitude in meters")
    timestamp = models.DateTimeField(help_text="Timestamp when position was recorded")
    odometer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Odometer reading in km")
    fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Fuel level percentage (0-100)")
    engine_status = models.CharField(
        max_length=20,
        choices=[
            ('on', 'Engine On'),
            ('off', 'Engine Off'),
            ('idle', 'Engine Idle'),
        ],
        default='off'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['vehicle', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.timestamp}"
