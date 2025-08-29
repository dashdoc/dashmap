from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'make', 'model', 'driver_name', 'company', 'is_active']
    search_fields = ['license_plate', 'driver_name', 'driver_email', 'make', 'model']
    list_filter = ['company', 'make', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('company', 'license_plate', 'make', 'model', 'year', 'capacity', 'is_active')
        }),
        ('Driver Information', {
            'fields': ('driver_name', 'driver_email', 'driver_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
