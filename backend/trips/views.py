from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
from django.db import models
import json
import random
from faker import Faker
from datetime import datetime, date, time
from .models import Trip, TripStop
from orders.models import Stop, Order

def get_orders_for_stop(stop):
    """Get all orders that use this stop as pickup or delivery"""
    orders = Order.objects.filter(
        models.Q(pickup_stop=stop) | models.Q(delivery_stop=stop)
    ).values('id', 'order_number', 'customer_name')
    return list(orders)


@method_decorator(csrf_exempt, name='dispatch')
class TripListCreateView(View):
    def get(self, request):
        trips = Trip.objects.select_related('vehicle', 'dispatcher').prefetch_related('trip_stops__stop').all()

        vehicle_id = request.GET.get('vehicle')
        company_id = request.GET.get('company')

        if vehicle_id:
            trips = trips.filter(vehicle_id=vehicle_id)
        if company_id:
            trips = trips.filter(vehicle__company_id=company_id)

        data = []
        for trip in trips:
            # Include trip_stops data in list view to eliminate N+1 queries
            trip_stops = []
            for trip_stop in trip.trip_stops.all().order_by('order'):
                trip_stops.append({
                    'id': trip_stop.id,
                    'stop': {
                        'id': trip_stop.stop.id,
                        'name': trip_stop.stop.name,
                        'address': trip_stop.stop.address,
                        'latitude': str(trip_stop.stop.latitude) if trip_stop.stop.latitude else None,
                        'longitude': str(trip_stop.stop.longitude) if trip_stop.stop.longitude else None,
                        'stop_type': trip_stop.stop.stop_type,
                        'contact_name': trip_stop.stop.contact_name,
                        'contact_phone': trip_stop.stop.contact_phone,
                        'notes': trip_stop.stop.notes
                    },
                    'order': trip_stop.order,
                    'planned_arrival_time': trip_stop.planned_arrival_time.isoformat(),
                    'actual_arrival_datetime': trip_stop.actual_arrival_datetime.isoformat() if trip_stop.actual_arrival_datetime else None,
                    'actual_departure_datetime': trip_stop.actual_departure_datetime.isoformat() if trip_stop.actual_departure_datetime else None,
                    'notes': trip_stop.notes,
                    'is_completed': trip_stop.is_completed,
                    'orders': get_orders_for_stop(trip_stop.stop)
                })

            data.append({
                'id': trip.id,
                'vehicle': trip.vehicle.id,
                'vehicle_license_plate': trip.vehicle.license_plate,
                'dispatcher': trip.dispatcher.id,
                'dispatcher_name': trip.dispatcher.get_full_name(),
                'name': trip.name,
                'status': trip.status,
                'planned_start_date': trip.planned_start_date.isoformat(),
                'planned_start_time': trip.planned_start_time.isoformat(),
                'actual_start_datetime': trip.actual_start_datetime.isoformat() if trip.actual_start_datetime else None,
                'actual_end_datetime': trip.actual_end_datetime.isoformat() if trip.actual_end_datetime else None,
                'notes': trip.notes,
                'driver_notified': trip.driver_notified,
                'trip_stops': trip_stops,
                'created_at': trip.created_at.isoformat(),
                'updated_at': trip.updated_at.isoformat()
            })
        return JsonResponse({'results': data})

    def post(self, request):
        try:
            data = json.loads(request.body)
            trip = Trip.objects.create(
                vehicle_id=data['vehicle'],
                dispatcher_id=data['dispatcher'],
                name=data['name'],
                status=data.get('status', 'draft'),
                planned_start_date=data['planned_start_date'],
                planned_start_time=data['planned_start_time'],
                notes=data.get('notes', '')
            )
            trip.refresh_from_db()
            return JsonResponse({
                'id': trip.id,
                'vehicle': trip.vehicle.id,
                'vehicle_license_plate': trip.vehicle.license_plate,
                'dispatcher': trip.dispatcher.id,
                'dispatcher_name': trip.dispatcher.get_full_name(),
                'name': trip.name,
                'status': trip.status,
                'planned_start_date': trip.planned_start_date.isoformat(),
                'planned_start_time': trip.planned_start_time.isoformat(),
                'actual_start_datetime': trip.actual_start_datetime.isoformat() if trip.actual_start_datetime else None,
                'actual_end_datetime': trip.actual_end_datetime.isoformat() if trip.actual_end_datetime else None,
                'notes': trip.notes,
                'driver_notified': trip.driver_notified,
                'created_at': trip.created_at.isoformat(),
                'updated_at': trip.updated_at.isoformat()
            }, status=201)
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class TripDetailView(View):
    def get_object(self, pk):
        try:
            return Trip.objects.select_related('vehicle', 'dispatcher').prefetch_related('trip_stops__stop').get(pk=pk)
        except Trip.DoesNotExist:
            return None

    def get(self, request, pk):
        trip = self.get_object(pk)
        if not trip:
            return JsonResponse({'error': 'Trip not found'}, status=404)

        trip_stops = []
        for trip_stop in trip.trip_stops.all().order_by('order'):
            trip_stops.append({
                'id': trip_stop.id,
                'stop': {
                    'id': trip_stop.stop.id,
                    'name': trip_stop.stop.name,
                    'address': trip_stop.stop.address,
                    'latitude': str(trip_stop.stop.latitude) if trip_stop.stop.latitude else None,
                    'longitude': str(trip_stop.stop.longitude) if trip_stop.stop.longitude else None,
                    'stop_type': trip_stop.stop.stop_type,
                    'contact_name': trip_stop.stop.contact_name,
                    'contact_phone': trip_stop.stop.contact_phone,
                    'notes': trip_stop.stop.notes
                },
                'order': trip_stop.order,
                'planned_arrival_time': trip_stop.planned_arrival_time.isoformat(),
                'actual_arrival_datetime': trip_stop.actual_arrival_datetime.isoformat() if trip_stop.actual_arrival_datetime else None,
                'actual_departure_datetime': trip_stop.actual_departure_datetime.isoformat() if trip_stop.actual_departure_datetime else None,
                'notes': trip_stop.notes,
                'is_completed': trip_stop.is_completed,
                'orders': get_orders_for_stop(trip_stop.stop)
            })

        return JsonResponse({
            'id': trip.id,
            'vehicle': trip.vehicle.id,
            'vehicle_license_plate': trip.vehicle.license_plate,
            'dispatcher': trip.dispatcher.id,
            'dispatcher_name': trip.dispatcher.get_full_name(),
            'name': trip.name,
            'status': trip.status,
            'planned_start_date': trip.planned_start_date.isoformat(),
            'planned_start_time': trip.planned_start_time.isoformat(),
            'actual_start_datetime': trip.actual_start_datetime.isoformat() if trip.actual_start_datetime else None,
            'actual_end_datetime': trip.actual_end_datetime.isoformat() if trip.actual_end_datetime else None,
            'notes': trip.notes,
            'driver_notified': trip.driver_notified,
            'trip_stops': trip_stops,
            'created_at': trip.created_at.isoformat(),
            'updated_at': trip.updated_at.isoformat()
        })

    def put(self, request, pk):
        trip = self.get_object(pk)
        if not trip:
            return JsonResponse({'error': 'Trip not found'}, status=404)

        try:
            data = json.loads(request.body)
            trip.vehicle_id = data.get('vehicle', trip.vehicle_id)
            trip.dispatcher_id = data.get('dispatcher', trip.dispatcher_id)
            trip.name = data.get('name', trip.name)
            trip.status = data.get('status', trip.status)

            # Parse date and time strings if provided
            if 'planned_start_date' in data:
                planned_start_date = data['planned_start_date']
                if isinstance(planned_start_date, str):
                    trip.planned_start_date = datetime.strptime(planned_start_date, '%Y-%m-%d').date()
                else:
                    trip.planned_start_date = planned_start_date

            if 'planned_start_time' in data:
                planned_start_time = data['planned_start_time']
                if isinstance(planned_start_time, str):
                    trip.planned_start_time = datetime.strptime(planned_start_time, '%H:%M:%S').time()
                else:
                    trip.planned_start_time = planned_start_time

            trip.notes = data.get('notes', trip.notes)
            trip.save()

            return JsonResponse({
                'id': trip.id,
                'vehicle': trip.vehicle.id,
                'vehicle_license_plate': trip.vehicle.license_plate,
                'dispatcher': trip.dispatcher.id,
                'dispatcher_name': trip.dispatcher.get_full_name(),
                'name': trip.name,
                'status': trip.status,
                'planned_start_date': trip.planned_start_date.isoformat(),
                'planned_start_time': trip.planned_start_time.isoformat(),
                'actual_start_datetime': trip.actual_start_datetime.isoformat() if trip.actual_start_datetime else None,
                'actual_end_datetime': trip.actual_end_datetime.isoformat() if trip.actual_end_datetime else None,
                'notes': trip.notes,
                'driver_notified': trip.driver_notified,
                'created_at': trip.created_at.isoformat(),
                'updated_at': trip.updated_at.isoformat()
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    def delete(self, request, pk):
        trip = self.get_object(pk)
        if not trip:
            return JsonResponse({'error': 'Trip not found'}, status=404)

        trip.delete()
        return JsonResponse({}, status=204)

@method_decorator(csrf_exempt, name='dispatch')
class TripNotifyDriverView(View):
    def post(self, request, pk):
        try:
            trip = Trip.objects.select_related('vehicle').prefetch_related('trip_stops__stop').get(pk=pk)
        except Trip.DoesNotExist:
            return JsonResponse({'error': 'Trip not found'}, status=404)

        if trip.driver_notified:
            return JsonResponse({'message': 'Driver already notified'}, status=400)

        subject = f'Trip Assignment: {trip.name}'
        message = f"""Hello {trip.vehicle.driver_name},

You have been assigned to a new trip:

Trip: {trip.name}
Vehicle: {trip.vehicle.license_plate}
Start Date: {trip.planned_start_date}
Start Time: {trip.planned_start_time}

Stops:"""

        for trip_stop in trip.trip_stops.all().order_by('order'):
            message += f"\n{trip_stop.order}. {trip_stop.stop.name} ({trip_stop.stop.stop_type}) - {trip_stop.planned_arrival_time}"
            message += f"\n   Address: {trip_stop.stop.address}"
            if trip_stop.notes:
                message += f"\n   Notes: {trip_stop.notes}"

        if trip.notes:
            message += f"\n\nTrip Notes: {trip.notes}"

        try:
            send_mail(
                subject,
                message,
                'dispatcher@company.com',
                [trip.vehicle.driver_email],
                fail_silently=False,
            )

            trip.driver_notified = True
            trip.save()

            return JsonResponse({'message': 'Driver notified successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class TripStopListCreateView(View):
    def get(self, request):
        trip_stops = TripStop.objects.select_related('trip', 'stop').all()

        trip_id = request.GET.get('trip')
        if trip_id:
            trip_stops = trip_stops.filter(trip_id=trip_id)

        data = []
        for trip_stop in trip_stops.order_by('order'):
            data.append({
                'id': trip_stop.id,
                'trip': trip_stop.trip.id,
                'stop': {
                    'id': trip_stop.stop.id,
                    'name': trip_stop.stop.name,
                    'address': trip_stop.stop.address,
                    'latitude': str(trip_stop.stop.latitude) if trip_stop.stop.latitude else None,
                    'longitude': str(trip_stop.stop.longitude) if trip_stop.stop.longitude else None,
                    'stop_type': trip_stop.stop.stop_type
                },
                'order': trip_stop.order,
                'planned_arrival_time': trip_stop.planned_arrival_time.isoformat(),
                'actual_arrival_datetime': trip_stop.actual_arrival_datetime.isoformat() if trip_stop.actual_arrival_datetime else None,
                'actual_departure_datetime': trip_stop.actual_departure_datetime.isoformat() if trip_stop.actual_departure_datetime else None,
                'notes': trip_stop.notes,
                'is_completed': trip_stop.is_completed
            })
        return JsonResponse({'results': data})

    def post(self, request):
        try:
            from django.db import transaction
            from django.db.utils import IntegrityError

            data = json.loads(request.body)
            trip_id = data['trip']
            requested_order = data['order']

            with transaction.atomic():
                # Check if the requested order already exists for this trip
                existing_stop = TripStop.objects.filter(
                    trip_id=trip_id,
                    order=requested_order
                ).first()

                if existing_stop:
                    # Shift existing stops to make room for the new stop
                    stops_to_shift = TripStop.objects.filter(
                        trip_id=trip_id,
                        order__gte=requested_order
                    ).order_by('order')

                    # Shift orders up by 1 starting from the end to avoid conflicts
                    for stop in reversed(list(stops_to_shift)):
                        stop.order += 1
                        stop.save()

                # Create the new trip stop
                trip_stop = TripStop.objects.create(
                    trip_id=trip_id,
                    stop_id=data['stop'],
                    order=requested_order,
                    planned_arrival_time=data['planned_arrival_time'],
                    notes=data.get('notes', '')
                )

            trip_stop.refresh_from_db()
            return JsonResponse({
                'id': trip_stop.id,
                'trip': trip_stop.trip.id,
                'stop': {
                    'id': trip_stop.stop.id,
                    'name': trip_stop.stop.name,
                    'address': trip_stop.stop.address,
                    'latitude': str(trip_stop.stop.latitude) if trip_stop.stop.latitude else None,
                    'longitude': str(trip_stop.stop.longitude) if trip_stop.stop.longitude else None,
                    'stop_type': trip_stop.stop.stop_type
                },
                'order': trip_stop.order,
                'planned_arrival_time': trip_stop.planned_arrival_time.isoformat(),
                'actual_arrival_datetime': trip_stop.actual_arrival_datetime.isoformat() if trip_stop.actual_arrival_datetime else None,
                'actual_departure_datetime': trip_stop.actual_departure_datetime.isoformat() if trip_stop.actual_departure_datetime else None,
                'notes': trip_stop.notes,
                'is_completed': trip_stop.is_completed
            }, status=201)
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        except IntegrityError as e:
            return JsonResponse({'error': 'Order conflict - unable to create trip stop'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class TripStopDetailView(View):
    def get_object(self, pk):
        try:
            return TripStop.objects.select_related('trip', 'stop').get(pk=pk)
        except TripStop.DoesNotExist:
            return None

    def get(self, request, pk):
        trip_stop = self.get_object(pk)
        if not trip_stop:
            return JsonResponse({'error': 'Trip stop not found'}, status=404)

        return JsonResponse({
            'id': trip_stop.id,
            'trip': trip_stop.trip.id,
            'stop': {
                'id': trip_stop.stop.id,
                'name': trip_stop.stop.name,
                'address': trip_stop.stop.address,
                'latitude': str(trip_stop.stop.latitude) if trip_stop.stop.latitude else None,
                'longitude': str(trip_stop.stop.longitude) if trip_stop.stop.longitude else None,
                'stop_type': trip_stop.stop.stop_type
            },
            'order': trip_stop.order,
            'planned_arrival_time': trip_stop.planned_arrival_time.isoformat(),
            'actual_arrival_datetime': trip_stop.actual_arrival_datetime.isoformat() if trip_stop.actual_arrival_datetime else None,
            'actual_departure_datetime': trip_stop.actual_departure_datetime.isoformat() if trip_stop.actual_departure_datetime else None,
            'notes': trip_stop.notes,
            'is_completed': trip_stop.is_completed
        })

    def put(self, request, pk):
        trip_stop = self.get_object(pk)
        if not trip_stop:
            return JsonResponse({'error': 'Trip stop not found'}, status=404)

        try:
            data = json.loads(request.body)
            trip_stop.order = data.get('order', trip_stop.order)
            trip_stop.planned_arrival_time = data.get('planned_arrival_time', trip_stop.planned_arrival_time)
            trip_stop.notes = data.get('notes', trip_stop.notes)
            trip_stop.is_completed = data.get('is_completed', trip_stop.is_completed)
            trip_stop.save()

            return JsonResponse({
                'id': trip_stop.id,
                'trip': trip_stop.trip.id,
                'stop': {
                    'id': trip_stop.stop.id,
                    'name': trip_stop.stop.name,
                    'address': trip_stop.stop.address,
                    'latitude': str(trip_stop.stop.latitude) if trip_stop.stop.latitude else None,
                    'longitude': str(trip_stop.stop.longitude) if trip_stop.stop.longitude else None,
                    'stop_type': trip_stop.stop.stop_type
                },
                'order': trip_stop.order,
                'planned_arrival_time': trip_stop.planned_arrival_time.isoformat(),
                'actual_arrival_datetime': trip_stop.actual_arrival_datetime.isoformat() if trip_stop.actual_arrival_datetime else None,
                'actual_departure_datetime': trip_stop.actual_departure_datetime.isoformat() if trip_stop.actual_departure_datetime else None,
                'notes': trip_stop.notes,
                'is_completed': trip_stop.is_completed
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    def delete(self, request, pk):
        trip_stop = self.get_object(pk)
        if not trip_stop:
            return JsonResponse({'error': 'Trip stop not found'}, status=404)

        trip = trip_stop.trip
        deleted_order = trip_stop.order

        # Delete the trip stop
        trip_stop.delete()

        # Reorder remaining stops to close gaps
        remaining_stops = TripStop.objects.filter(
            trip=trip,
            order__gt=deleted_order
        ).order_by('order')

        # Shift all stops with higher order numbers down by 1
        for stop in remaining_stops:
            stop.order -= 1
            stop.save()

        return JsonResponse({}, status=204)

@method_decorator(csrf_exempt, name='dispatch')
class TripStopReorderView(View):
    def post(self, request, trip_pk):
        """Reorder trip stops for a given trip"""
        try:
            from django.db import transaction
            import logging
            logger = logging.getLogger(__name__)

            data = json.loads(request.body)
            new_orders = data.get('orders', [])  # Expected format: [{'id': stop_id, 'order': new_order}, ...]

            logger.info(f"Reordering stops for trip {trip_pk}: {new_orders}")

            if not new_orders:
                return JsonResponse({'error': 'No orders provided'}, status=400)

            # Verify the trip exists
            try:
                trip = Trip.objects.get(pk=trip_pk)
            except Trip.DoesNotExist:
                return JsonResponse({'error': 'Trip not found'}, status=404)

            with transaction.atomic():
                # Validate that all provided stop IDs belong to this trip
                provided_stop_ids = [item['id'] for item in new_orders]
                existing_stops = TripStop.objects.filter(
                    trip=trip,
                    id__in=provided_stop_ids
                )

                if len(existing_stops) != len(provided_stop_ids):
                    return JsonResponse({'error': 'Some trip stops do not belong to this trip'}, status=400)

                # First, set all orders to very high values to avoid constraint conflicts
                # Use values starting from 10000 to avoid conflicts with existing orders
                for i, order_item in enumerate(new_orders):
                    trip_stop = TripStop.objects.get(id=order_item['id'], trip=trip)
                    trip_stop.order = 10000 + i  # Use high values temporarily
                    trip_stop.save()

                # Then set the final order values
                for order_item in new_orders:
                    trip_stop = TripStop.objects.get(id=order_item['id'], trip=trip)
                    trip_stop.order = order_item['order']
                    trip_stop.save()

            # Return updated trip stops
            updated_stops = TripStop.objects.filter(trip=trip).order_by('order')
            data = []
            for trip_stop in updated_stops:
                data.append({
                    'id': trip_stop.id,
                    'trip': trip_stop.trip.id,
                    'stop': {
                        'id': trip_stop.stop.id,
                        'name': trip_stop.stop.name,
                        'address': trip_stop.stop.address,
                        'latitude': str(trip_stop.stop.latitude) if trip_stop.stop.latitude else None,
                        'longitude': str(trip_stop.stop.longitude) if trip_stop.stop.longitude else None,
                        'stop_type': trip_stop.stop.stop_type
                    },
                    'order': trip_stop.order,
                    'planned_arrival_time': trip_stop.planned_arrival_time.isoformat(),
                    'actual_arrival_datetime': trip_stop.actual_arrival_datetime.isoformat() if trip_stop.actual_arrival_datetime else None,
                    'actual_departure_datetime': trip_stop.actual_departure_datetime.isoformat() if trip_stop.actual_departure_datetime else None,
                    'notes': trip_stop.notes,
                    'is_completed': trip_stop.is_completed
                })

            return JsonResponse({'results': data}, status=200)

        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': 'Invalid data format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
