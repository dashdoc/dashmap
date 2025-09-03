from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import OuterRef, Subquery
import json
import random
from datetime import datetime, timedelta
from .models import Position
from vehicles.models import Vehicle

@method_decorator(csrf_exempt, name='dispatch')
class PositionListCreateView(View):
    def get(self, request):
        positions = Position.objects.select_related('vehicle', 'vehicle__company').all()

        vehicle_id = request.GET.get('vehicle')
        if vehicle_id:
            positions = positions.filter(vehicle_id=vehicle_id)

        data = []
        for position in positions:
            data.append({
                'id': position.id,
                'vehicle_id': position.vehicle.id,
                'vehicle_license_plate': position.vehicle.license_plate,
                'latitude': f"{position.latitude:.7f}",
                'longitude': f"{position.longitude:.7f}",
                'speed': f"{position.speed:.2f}",
                'heading': f"{position.heading:.2f}",
                'altitude': f"{position.altitude:.2f}" if position.altitude else None,
                'timestamp': position.timestamp.isoformat(),
                'odometer': f"{position.odometer:.2f}" if position.odometer else None,
                'fuel_level': f"{position.fuel_level:.2f}" if position.fuel_level else None,
                'engine_status': position.engine_status,
                'created_at': position.created_at.isoformat()
            })
        return JsonResponse({'results': data})

    def post(self, request):
        try:
            data = json.loads(request.body)

            # Verify vehicle exists before creating position
            try:
                vehicle = Vehicle.objects.get(id=data['vehicle_id'])
            except Vehicle.DoesNotExist:
                return JsonResponse({'error': 'Vehicle not found'}, status=400)

            # Parse timestamp if provided, otherwise use current time
            timestamp = data.get('timestamp')
            if timestamp:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                timestamp = timezone.now()

            position = Position.objects.create(
                vehicle=vehicle,
                latitude=data['latitude'],
                longitude=data['longitude'],
                speed=data['speed'],
                heading=data['heading'],
                altitude=data.get('altitude'),
                timestamp=timestamp,
                odometer=data.get('odometer'),
                fuel_level=data.get('fuel_level'),
                engine_status=data.get('engine_status', 'off')
            )

            return JsonResponse({
                'id': position.id,
                'vehicle_id': position.vehicle.id,
                'vehicle_license_plate': position.vehicle.license_plate,
                'latitude': f"{position.latitude:.7f}",
                'longitude': f"{position.longitude:.7f}",
                'speed': f"{position.speed:.2f}",
                'heading': f"{position.heading:.2f}",
                'altitude': f"{position.altitude:.2f}" if position.altitude else None,
                'timestamp': position.timestamp.isoformat(),
                'odometer': f"{position.odometer:.2f}" if position.odometer else None,
                'fuel_level': f"{position.fuel_level:.2f}" if position.fuel_level else None,
                'engine_status': position.engine_status,
                'created_at': position.created_at.isoformat()
            }, status=201)
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class GenerateFakeView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            vehicle_id = data['vehicle_id']
            count = data.get('count', 10)

            # Verify vehicle exists
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
            except Vehicle.DoesNotExist:
                return JsonResponse({'error': 'Vehicle not found'}, status=404)

            # Base coordinates (you can adjust these as needed)
            base_lat = data.get('base_latitude', 40.7589)  # NYC area
            base_lng = data.get('base_longitude', -73.9851)

            positions = []
            current_time = timezone.now()

            # Generate random positions in a realistic pattern
            for i in range(count):
                # Create positions going back in time
                timestamp = current_time - timedelta(minutes=i * 5)

                # Add some randomness to coordinates (within ~5km radius)
                lat_offset = random.uniform(-0.05, 0.05)
                lng_offset = random.uniform(-0.05, 0.05)

                position = Position.objects.create(
                    vehicle=vehicle,
                    latitude=base_lat + lat_offset,
                    longitude=base_lng + lng_offset,
                    speed=random.uniform(0, 80),  # 0-80 km/h
                    heading=random.uniform(0, 360),
                    altitude=random.uniform(0, 200) if random.random() > 0.5 else None,
                    timestamp=timestamp,
                    odometer=random.uniform(10000, 50000) if random.random() > 0.3 else None,
                    fuel_level=random.uniform(10, 100) if random.random() > 0.2 else None,
                    engine_status=random.choice(['on', 'off', 'idle'])
                )
                positions.append(position)

            return JsonResponse({
                'message': f'Generated {count} fake positions for vehicle {vehicle.license_plate}',
                'count': count,
                'vehicle_id': vehicle_id
            }, status=201)

        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LatestPositionsView(View):
    def get(self, request):
        """Get the latest position for each vehicle"""
        # Get latest position for each vehicle using subquery
        latest_positions_subquery = Position.objects.filter(
            vehicle=OuterRef('vehicle')
        ).order_by('-timestamp').values('id')[:1]

        latest_positions = Position.objects.filter(
            id__in=Subquery(latest_positions_subquery)
        ).select_related('vehicle', 'vehicle__company')

        data = []
        for position in latest_positions:
            data.append({
                'id': position.id,
                'vehicle_id': position.vehicle.id,
                'vehicle_license_plate': position.vehicle.license_plate,
                'vehicle_make_model': f"{position.vehicle.make} {position.vehicle.model}",
                'latitude': f"{position.latitude:.7f}",
                'longitude': f"{position.longitude:.7f}",
                'speed': f"{position.speed:.2f}",
                'heading': f"{position.heading:.2f}",
                'altitude': f"{position.altitude:.2f}" if position.altitude else None,
                'timestamp': position.timestamp.isoformat(),
                'odometer': f"{position.odometer:.2f}" if position.odometer else None,
                'fuel_level': f"{position.fuel_level:.2f}" if position.fuel_level else None,
                'engine_status': position.engine_status,
                'created_at': position.created_at.isoformat()
            })

        return JsonResponse({'results': data})
