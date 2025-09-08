from django.db import models
from django.contrib.auth.models import User


class Stop(models.Model):
    STOP_TYPES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='stops', null=True, blank=True)
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
        return f"{self.name} ({self.stop_type}) - {self.order.order_number}"


class Order(models.Model):
    GOODS_TYPES = [
        ('standard', 'Standard'),
        ('fragile', 'Fragile'),
        ('hazmat', 'Hazardous Materials'),
        ('refrigerated', 'Refrigerated'),
        ('oversized', 'Oversized'),
    ]

    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # Customer Information
    customer_name = models.CharField(max_length=200)
    customer_company = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)


    # Goods Information
    goods_description = models.TextField()
    goods_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in kg
    goods_volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # in m³
    goods_type = models.CharField(max_length=20, choices=GOODS_TYPES, default='standard')
    special_instructions = models.TextField(blank=True)

    # Order Metadata
    order_number = models.CharField(unique=True, max_length=50)  # Auto-generated like ORD-2024-0001
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    requested_pickup_date = models.DateField(null=True, blank=True)
    requested_delivery_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number like ORD-2024-0001
            from datetime import datetime
            year = datetime.now().year
            last_order = Order.objects.filter(
                order_number__startswith=f'ORD-{year}-'
            ).order_by('order_number').last()

            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.order_number = f'ORD-{year}-{new_num:04d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"
