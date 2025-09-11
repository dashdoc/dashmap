from django.contrib import admin
from .models import Stop, Trip, TripStop

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ['name', 'stop_type', 'contact_name', 'created_at']
    search_fields = ['name', 'address', 'contact_name']
    list_filter = ['stop_type', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

class TripStopInline(admin.TabularInline):
    model = TripStop
    extra = 0
    ordering = ['sequence']
    fields = ['stop', 'sequence', 'planned_arrival_time', 'is_completed', 'notes']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle', 'dispatcher', 'status', 'planned_start_date', 'driver_notified']
    search_fields = ['name', 'vehicle__license_plate', 'dispatcher__username']
    list_filter = ['status', 'vehicle__company', 'planned_start_date', 'driver_notified']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TripStopInline]
    fieldsets = (
        ('Trip Information', {
            'fields': ('name', 'vehicle', 'dispatcher', 'status')
        }),
        ('Scheduling', {
            'fields': ('planned_start_date', 'planned_start_time', 'actual_start_datetime', 'actual_end_datetime')
        }),
        ('Communication', {
            'fields': ('driver_notified', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TripStop)
class TripStopAdmin(admin.ModelAdmin):
    list_display = ['trip', 'stop', 'sequence', 'planned_arrival_time', 'is_completed']
    search_fields = ['trip__name', 'stop__name']
    list_filter = ['is_completed', 'trip__status']
    ordering = ['trip', 'sequence']
