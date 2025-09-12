from django.db import models
from django.utils import timezone
from companies.models import Company


class Vehicle(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="vehicles"
    )
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    capacity = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Capacity in tons"
    )
    driver_name = models.CharField(max_length=100)
    driver_email = models.EmailField()
    driver_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return f"{self.license_plate} - {self.driver_name}"
