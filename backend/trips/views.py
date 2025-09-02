from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
import json
import random
from faker import Faker
from datetime import datetime, date, time
from .models import Stop, Trip, TripStop

@method_decorator(csrf_exempt, name='dispatch')
class StopListCreateView(View):
    def get(self, request):
        stops = Stop.objects.all()
        data = []
        for stop in stops:
            data.append({
                'id': stop.id,
                'name': stop.name,
                'address': stop.address,
                'latitude': str(stop.latitude) if stop.latitude else None,
                'longitude': str(stop.longitude) if stop.longitude else None,
                'stop_type': stop.stop_type,
                'contact_name': stop.contact_name,
                'contact_phone': stop.contact_phone,
                'notes': stop.notes,
                'created_at': stop.created_at.isoformat(),
                'updated_at': stop.updated_at.isoformat()
            })
        return JsonResponse({'results': data})

    def post(self, request):
        try:
            data = json.loads(request.body)
            stop = Stop.objects.create(
                name=data['name'],
                address=data['address'],
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                stop_type=data['stop_type'],
                contact_name=data.get('contact_name', ''),
                contact_phone=data.get('contact_phone', ''),
                notes=data.get('notes', '')
            )
            return JsonResponse({
                'id': stop.id,
                'name': stop.name,
                'address': stop.address,
                'latitude': str(stop.latitude) if stop.latitude else None,
                'longitude': str(stop.longitude) if stop.longitude else None,
                'stop_type': stop.stop_type,
                'contact_name': stop.contact_name,
                'contact_phone': stop.contact_phone,
                'notes': stop.notes,
                'created_at': stop.created_at.isoformat(),
                'updated_at': stop.updated_at.isoformat()
            }, status=201)
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class StopDetailView(View):
    def get_object(self, pk):
        try:
            return Stop.objects.get(pk=pk)
        except Stop.DoesNotExist:
            return None

    def get(self, request, pk):
        stop = self.get_object(pk)
        if not stop:
            return JsonResponse({'error': 'Stop not found'}, status=404)

        return JsonResponse({
            'id': stop.id,
            'name': stop.name,
            'address': stop.address,
            'latitude': str(stop.latitude) if stop.latitude else None,
            'longitude': str(stop.longitude) if stop.longitude else None,
            'stop_type': stop.stop_type,
            'contact_name': stop.contact_name,
            'contact_phone': stop.contact_phone,
            'notes': stop.notes,
            'created_at': stop.created_at.isoformat(),
            'updated_at': stop.updated_at.isoformat()
        })

    def put(self, request, pk):
        stop = self.get_object(pk)
        if not stop:
            return JsonResponse({'error': 'Stop not found'}, status=404)

        try:
            data = json.loads(request.body)
            stop.name = data.get('name', stop.name)
            stop.address = data.get('address', stop.address)
            stop.latitude = data.get('latitude', stop.latitude)
            stop.longitude = data.get('longitude', stop.longitude)
            stop.stop_type = data.get('stop_type', stop.stop_type)
            stop.contact_name = data.get('contact_name', stop.contact_name)
            stop.contact_phone = data.get('contact_phone', stop.contact_phone)
            stop.notes = data.get('notes', stop.notes)
            stop.save()

            return JsonResponse({
                'id': stop.id,
                'name': stop.name,
                'address': stop.address,
                'latitude': str(stop.latitude) if stop.latitude else None,
                'longitude': str(stop.longitude) if stop.longitude else None,
                'stop_type': stop.stop_type,
                'contact_name': stop.contact_name,
                'contact_phone': stop.contact_phone,
                'notes': stop.notes,
                'created_at': stop.created_at.isoformat(),
                'updated_at': stop.updated_at.isoformat()
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    def delete(self, request, pk):
        stop = self.get_object(pk)
        if not stop:
            return JsonResponse({'error': 'Stop not found'}, status=404)

        stop.delete()
        return JsonResponse({}, status=204)

@method_decorator(csrf_exempt, name='dispatch')
class TripListCreateView(View):
    def get(self, request):
        trips = Trip.objects.select_related('vehicle', 'dispatcher').all()

        vehicle_id = request.GET.get('vehicle')
        company_id = request.GET.get('company')

        if vehicle_id:
            trips = trips.filter(vehicle_id=vehicle_id)
        if company_id:
            trips = trips.filter(vehicle__company_id=company_id)

        data = []
        for trip in trips:
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
                'is_completed': trip_stop.is_completed
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
            data = json.loads(request.body)
            trip_stop = TripStop.objects.create(
                trip_id=data['trip'],
                stop_id=data['stop'],
                order=data['order'],
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

        trip_stop.delete()
        return JsonResponse({}, status=204)

@method_decorator(csrf_exempt, name='dispatch')
class GetOrdersView(View):
    def post(self, request):
        """Generate random orders (stops) with faker data"""
        try:
            fake = Faker()

            # Generate 3-8 random orders
            num_orders = random.randint(3, 8)
            created_stops = []

            for i in range(num_orders):
                # Randomly choose stop type
                stop_type = random.choice(['loading', 'unloading'])

                # Generate realistic business names and addresses
                if stop_type == 'loading':
                    name_prefixes = ['Warehouse', 'Distribution Center', 'Loading Dock', 'Supply Hub']
                    name = f"{random.choice(name_prefixes)} {fake.random_letter().upper()}"
                else:
                    name_prefixes = ['Store', 'Market', 'Shop', 'Outlet', 'Center']
                    name = f"{fake.company()} {random.choice(name_prefixes)}"

                # Create the stop
                stop = Stop.objects.create(
                    name=name,
                    address=f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()} {fake.zipcode()}",
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                    stop_type=stop_type,
                    contact_name=fake.name(),
                    contact_phone=fake.phone_number()[:15],  # Limit to 15 chars to fit model
                    notes=fake.sentence() if random.choice([True, False]) else ""
                )

                created_stops.append({
                    'id': stop.id,
                    'name': stop.name,
                    'address': stop.address,
                    'latitude': str(stop.latitude) if stop.latitude else None,
                    'longitude': str(stop.longitude) if stop.longitude else None,
                    'stop_type': stop.stop_type,
                    'contact_name': stop.contact_name,
                    'contact_phone': stop.contact_phone,
                    'notes': stop.notes,
                    'created_at': stop.created_at.isoformat(),
                    'updated_at': stop.updated_at.isoformat()
                })

            return JsonResponse({
                'message': f'Successfully created {num_orders} new orders',
                'created_stops': created_stops
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
