from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import random
from faker import Faker
from .models import Stop, Order


@method_decorator(csrf_exempt, name='dispatch')
class OrderListCreateView(View):
    def get(self, request):
        orders = Order.objects.prefetch_related('stops').all()
        data = []
        for order in orders:
            stops = list(order.stops.all())
            pickup_stops = [s for s in stops if s.stop_type in ['pickup', 'loading']]
            delivery_stops = [s for s in stops if s.stop_type in ['delivery', 'unloading']]

            data.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'stops': [{
                    'id': stop.id,
                    'name': stop.name,
                    'address': stop.address,
                    'latitude': str(stop.latitude) if stop.latitude else None,
                    'longitude': str(stop.longitude) if stop.longitude else None,
                    'stop_type': stop.stop_type,
                    'contact_name': stop.contact_name,
                    'contact_phone': stop.contact_phone,
                    'notes': stop.notes,
                } for stop in stops],
                'pickup_stop': {
                    'id': pickup_stops[0].id,
                    'name': pickup_stops[0].name,
                    'address': pickup_stops[0].address,
                    'latitude': str(pickup_stops[0].latitude) if pickup_stops[0].latitude else None,
                    'longitude': str(pickup_stops[0].longitude) if pickup_stops[0].longitude else None,
                    'stop_type': pickup_stops[0].stop_type,
                    'contact_name': pickup_stops[0].contact_name,
                    'contact_phone': pickup_stops[0].contact_phone,
                    'notes': pickup_stops[0].notes,
                } if pickup_stops else None,
                'delivery_stop': {
                    'id': delivery_stops[0].id,
                    'name': delivery_stops[0].name,
                    'address': delivery_stops[0].address,
                    'latitude': str(delivery_stops[0].latitude) if delivery_stops[0].latitude else None,
                    'longitude': str(delivery_stops[0].longitude) if delivery_stops[0].longitude else None,
                    'stop_type': delivery_stops[0].stop_type,
                    'contact_name': delivery_stops[0].contact_name,
                    'contact_phone': delivery_stops[0].contact_phone,
                    'notes': delivery_stops[0].notes,
                } if delivery_stops else None,
                'goods_description': order.goods_description,
                'goods_weight': str(order.goods_weight) if order.goods_weight else None,
                'goods_volume': str(order.goods_volume) if order.goods_volume else None,
                'goods_type': order.goods_type,
                'special_instructions': order.special_instructions,
                'status': order.status,
                'requested_pickup_date': order.requested_pickup_date.isoformat() if order.requested_pickup_date else None,
                'requested_delivery_date': order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            })
        return JsonResponse({'results': data})

    def post(self, request):
        try:
            data = json.loads(request.body)
            order = Order.objects.create(
                customer_name=data['customer_name'],
                customer_company=data.get('customer_company', ''),
                customer_email=data.get('customer_email', ''),
                customer_phone=data.get('customer_phone', ''),
                goods_description=data['goods_description'],
                goods_weight=data.get('goods_weight'),
                goods_volume=data.get('goods_volume'),
                goods_type=data.get('goods_type', 'standard'),
                special_instructions=data.get('special_instructions', ''),
                requested_pickup_date=data.get('requested_pickup_date'),
                requested_delivery_date=data.get('requested_delivery_date')
            )

            # Create stops if provided
            if 'stops' in data:
                for stop_data in data['stops']:
                    Stop.objects.create(
                        order=order,
                        name=stop_data['name'],
                        address=stop_data['address'],
                        latitude=stop_data.get('latitude'),
                        longitude=stop_data.get('longitude'),
                        stop_type=stop_data['stop_type'],
                        contact_name=stop_data.get('contact_name', ''),
                        contact_phone=stop_data.get('contact_phone', ''),
                        notes=stop_data.get('notes', '')
                    )

            order.refresh_from_db()
            stops = list(order.stops.all())

            return JsonResponse({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'stops': [{
                    'id': stop.id,
                    'name': stop.name,
                    'address': stop.address,
                    'latitude': str(stop.latitude) if stop.latitude else None,
                    'longitude': str(stop.longitude) if stop.longitude else None,
                    'stop_type': stop.stop_type,
                    'contact_name': stop.contact_name,
                    'contact_phone': stop.contact_phone,
                    'notes': stop.notes,
                } for stop in stops],
                'goods_description': order.goods_description,
                'goods_weight': str(order.goods_weight) if order.goods_weight else None,
                'goods_volume': str(order.goods_volume) if order.goods_volume else None,
                'goods_type': order.goods_type,
                'special_instructions': order.special_instructions,
                'status': order.status,
                'requested_pickup_date': order.requested_pickup_date.isoformat() if order.requested_pickup_date else None,
                'requested_delivery_date': order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }, status=201)
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class OrderDetailView(View):
    def get_object(self, pk):
        try:
            return Order.objects.prefetch_related('stops').get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)

        stops = list(order.stops.all())
        pickup_stops = [s for s in stops if s.stop_type in ['pickup', 'loading']]
        delivery_stops = [s for s in stops if s.stop_type in ['delivery', 'unloading']]

        return JsonResponse({
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.customer_name,
            'customer_company': order.customer_company,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
            'stops': [{
                'id': stop.id,
                'name': stop.name,
                'address': stop.address,
                'latitude': str(stop.latitude) if stop.latitude else None,
                'longitude': str(stop.longitude) if stop.longitude else None,
                'stop_type': stop.stop_type,
                'contact_name': stop.contact_name,
                'contact_phone': stop.contact_phone,
                'notes': stop.notes,
            } for stop in stops],
            'pickup_stop': {
                'id': pickup_stops[0].id,
                'name': pickup_stops[0].name,
                'address': pickup_stops[0].address,
                'latitude': str(pickup_stops[0].latitude) if pickup_stops[0].latitude else None,
                'longitude': str(pickup_stops[0].longitude) if pickup_stops[0].longitude else None,
                'stop_type': pickup_stops[0].stop_type,
                'contact_name': pickup_stops[0].contact_name,
                'contact_phone': pickup_stops[0].contact_phone,
                'notes': pickup_stops[0].notes,
            } if pickup_stops else None,
            'delivery_stop': {
                'id': delivery_stops[0].id,
                'name': delivery_stops[0].name,
                'address': delivery_stops[0].address,
                'latitude': str(delivery_stops[0].latitude) if delivery_stops[0].latitude else None,
                'longitude': str(delivery_stops[0].longitude) if delivery_stops[0].longitude else None,
                'stop_type': delivery_stops[0].stop_type,
                'contact_name': delivery_stops[0].contact_name,
                'contact_phone': delivery_stops[0].contact_phone,
                'notes': delivery_stops[0].notes,
            } if delivery_stops else None,
            'goods_description': order.goods_description,
            'goods_weight': str(order.goods_weight) if order.goods_weight else None,
            'goods_volume': str(order.goods_volume) if order.goods_volume else None,
            'goods_type': order.goods_type,
            'special_instructions': order.special_instructions,
            'status': order.status,
            'requested_pickup_date': order.requested_pickup_date.isoformat() if order.requested_pickup_date else None,
            'requested_delivery_date': order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat()
        })

    def put(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)

        try:
            data = json.loads(request.body)
            order.customer_name = data.get('customer_name', order.customer_name)
            order.customer_company = data.get('customer_company', order.customer_company)
            order.customer_email = data.get('customer_email', order.customer_email)
            order.customer_phone = data.get('customer_phone', order.customer_phone)

            # Handle stops updates if provided
            if 'stops' in data:
                # Clear existing stops and create new ones
                order.stops.all().delete()
                for stop_data in data['stops']:
                    Stop.objects.create(
                        order=order,
                        name=stop_data['name'],
                        address=stop_data['address'],
                        latitude=stop_data.get('latitude'),
                        longitude=stop_data.get('longitude'),
                        stop_type=stop_data['stop_type'],
                        contact_name=stop_data.get('contact_name', ''),
                        contact_phone=stop_data.get('contact_phone', ''),
                        notes=stop_data.get('notes', '')
                    )

            order.goods_description = data.get('goods_description', order.goods_description)
            order.goods_weight = data.get('goods_weight', order.goods_weight)
            order.goods_volume = data.get('goods_volume', order.goods_volume)
            order.goods_type = data.get('goods_type', order.goods_type)
            order.special_instructions = data.get('special_instructions', order.special_instructions)
            order.status = data.get('status', order.status)

            if 'requested_pickup_date' in data:
                order.requested_pickup_date = data['requested_pickup_date']
            if 'requested_delivery_date' in data:
                order.requested_delivery_date = data['requested_delivery_date']

            order.save()
            order.refresh_from_db()
            stops = list(order.stops.all())

            return JsonResponse({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'stops': [{
                    'id': stop.id,
                    'name': stop.name,
                    'address': stop.address,
                    'latitude': str(stop.latitude) if stop.latitude else None,
                    'longitude': str(stop.longitude) if stop.longitude else None,
                    'stop_type': stop.stop_type,
                    'contact_name': stop.contact_name,
                    'contact_phone': stop.contact_phone,
                    'notes': stop.notes,
                } for stop in stops],
                'goods_description': order.goods_description,
                'goods_weight': str(order.goods_weight) if order.goods_weight else None,
                'goods_volume': str(order.goods_volume) if order.goods_volume else None,
                'goods_type': order.goods_type,
                'special_instructions': order.special_instructions,
                'status': order.status,
                'requested_pickup_date': order.requested_pickup_date.isoformat() if order.requested_pickup_date else None,
                'requested_delivery_date': order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    def delete(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)

        order.delete()
        return JsonResponse({}, status=204)


@method_decorator(csrf_exempt, name='dispatch')
class GenerateFakeOrdersView(View):
    def post(self, request):
        """Generate random orders with faker data"""
        try:
            fake = Faker()

            # Generate 2-5 random orders
            num_orders = random.randint(2, 5)
            created_orders = []

            for i in range(num_orders):
                # Generate realistic goods data
                goods_types = ['standard', 'fragile', 'hazmat', 'refrigerated', 'oversized']
                goods_descriptions = [
                    'Electronics components', 'Automotive parts', 'Food products',
                    'Pharmaceutical supplies', 'Construction materials', 'Textiles',
                    'Machinery equipment', 'Chemical products', 'Furniture items'
                ]

                order = Order.objects.create(
                    customer_name=fake.name(),
                    customer_company=fake.company(),
                    customer_email=fake.email(),
                    customer_phone=fake.phone_number()[:20],
                    goods_description=random.choice(goods_descriptions),
                    goods_weight=random.uniform(50, 5000),  # 50kg to 5 tons
                    goods_volume=random.uniform(1, 50),     # 1 to 50 m³
                    goods_type=random.choice(goods_types),
                    special_instructions=fake.sentence() if random.choice([True, False]) else "",
                    status='pending'
                )

                # Create pickup stop
                pickup_coords = fake.local_latlng(country_code='FR')
                pickup_stop = Stop.objects.create(
                    order=order,
                    name=f"{fake.company()} Warehouse",
                    address=fake.address(),
                    latitude=pickup_coords[0],
                    longitude=pickup_coords[1],
                    stop_type='pickup',
                    contact_name=fake.name(),
                    contact_phone=fake.phone_number()[:20],
                    notes='Pickup location'
                )

                # Create delivery stop
                delivery_coords = fake.local_latlng(country_code='FR')
                delivery_stop = Stop.objects.create(
                    order=order,
                    name=f"{fake.company()} Distribution Center",
                    address=fake.address(),
                    latitude=delivery_coords[0],
                    longitude=delivery_coords[1],
                    stop_type='delivery',
                    contact_name=fake.name(),
                    contact_phone=fake.phone_number()[:20],
                    notes='Delivery location'
                )

                created_orders.append({
                    'id': order.id,
                    'order_number': order.order_number,
                    'customer_name': order.customer_name,
                    'customer_company': order.customer_company,
                    'pickup_stop_name': pickup_stop.name,
                    'delivery_stop_name': delivery_stop.name,
                    'goods_description': order.goods_description,
                    'goods_weight': str(order.goods_weight),
                    'goods_type': order.goods_type,
                    'status': order.status
                })

            return JsonResponse({
                'message': f'Successfully created {num_orders} new orders',
                'created_orders': created_orders
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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
                notes=data.get('notes', ''),
                order_id=data.get('order') if data.get('order') else None
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
        except (KeyError, json.JSONDecodeError, ValueError) as e:
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
            if 'order' in data:
                stop.order_id = data['order'] if data['order'] else None

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
class GenerateFakeStopsView(View):
    def post(self, request):
        """Generate random stops with faker data"""
        try:
            fake = Faker(['fr_FR', 'en_US', 'de_DE', 'it_IT', 'es_ES'])

            # Generate 3-8 random stops
            num_stops = random.randint(3, 8)
            created_stops = []

            stop_types = ['loading', 'unloading']

            for i in range(num_stops):
                coords = fake.local_latlng(country_code='FR')

                # Generate address with proper comma-separated format
                address = f"{fake.street_address()}, {fake.city()}, {fake.state()} {fake.postcode()}"

                stop = Stop.objects.create(
                    name=f"{fake.company()} {random.choice(['Warehouse', 'Distribution Center', 'Loading Dock', 'Supply Hub'])}",
                    address=address,
                    latitude=coords[0],
                    longitude=coords[1],
                    stop_type=random.choice(stop_types),
                    contact_name=fake.name(),
                    contact_phone=fake.phone_number()[:15],  # Truncate to 15 chars max
                    notes=fake.sentence() if random.choice([True, False]) else ""
                )

                created_stops.append({
                    'id': stop.id,
                    'name': stop.name,
                    'address': stop.address,
                    'latitude': str(stop.latitude),
                    'longitude': str(stop.longitude),
                    'stop_type': stop.stop_type,
                    'contact_name': stop.contact_name,
                    'contact_phone': stop.contact_phone,
                    'notes': stop.notes,
                    'created_at': stop.created_at.isoformat(),
                    'updated_at': stop.updated_at.isoformat()
                })

            return JsonResponse({
                'message': f'Successfully created {num_stops} new stops',
                'created_stops': created_stops
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
