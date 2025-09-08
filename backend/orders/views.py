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

        # Filter for orders available for trip assignment
        if request.GET.get('available_for_trip') == 'true':
            # Only include orders with status 'pending' that don't have stops assigned to trips
            from trips.models import TripStop
            orders = orders.filter(status='pending')
            # Exclude orders whose stops are already in trip_stops
            assigned_stop_ids = TripStop.objects.values_list('stop_id', flat=True)
            orders = orders.exclude(stops__id__in=assigned_stop_ids)
        data = []
        for order in orders:
            stops = list(order.stops.all())
            pickup_stops = [s for s in stops if s.stop_type == 'pickup']
            delivery_stops = [s for s in stops if s.stop_type == 'delivery']

            data.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
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

            # Create pickup and delivery stops if provided
            if 'pickup_stop' in data:
                Stop.objects.create(
                    order=order,
                    name=data['pickup_stop']['name'],
                    address=data['pickup_stop']['address'],
                    latitude=data['pickup_stop'].get('latitude'),
                    longitude=data['pickup_stop'].get('longitude'),
                    stop_type=data['pickup_stop'].get('stop_type', 'pickup'),
                    contact_name=data['pickup_stop'].get('contact_name', ''),
                    contact_phone=data['pickup_stop'].get('contact_phone', ''),
                    notes=data['pickup_stop'].get('notes', '')
                )

            if 'delivery_stop' in data:
                Stop.objects.create(
                    order=order,
                    name=data['delivery_stop']['name'],
                    address=data['delivery_stop']['address'],
                    latitude=data['delivery_stop'].get('latitude'),
                    longitude=data['delivery_stop'].get('longitude'),
                    stop_type=data['delivery_stop'].get('stop_type', 'delivery'),
                    contact_name=data['delivery_stop'].get('contact_name', ''),
                    contact_phone=data['delivery_stop'].get('contact_phone', ''),
                    notes=data['delivery_stop'].get('notes', '')
                )

            order.refresh_from_db()
            stops = list(order.stops.all())
            pickup_stops = [s for s in stops if s.stop_type == 'pickup']
            delivery_stops = [s for s in stops if s.stop_type == 'delivery']

            return JsonResponse({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
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

            # Handle pickup and delivery stop updates if provided
            if 'pickup_stop' in data or 'delivery_stop' in data:
                # Clear existing stops and create new ones
                order.stops.all().delete()

                if 'pickup_stop' in data:
                    Stop.objects.create(
                        order=order,
                        name=data['pickup_stop']['name'],
                        address=data['pickup_stop']['address'],
                        latitude=data['pickup_stop'].get('latitude'),
                        longitude=data['pickup_stop'].get('longitude'),
                        stop_type=data['pickup_stop'].get('stop_type', 'pickup'),
                        contact_name=data['pickup_stop'].get('contact_name', ''),
                        contact_phone=data['pickup_stop'].get('contact_phone', ''),
                        notes=data['pickup_stop'].get('notes', '')
                    )

                if 'delivery_stop' in data:
                    Stop.objects.create(
                        order=order,
                        name=data['delivery_stop']['name'],
                        address=data['delivery_stop']['address'],
                        latitude=data['delivery_stop'].get('latitude'),
                        longitude=data['delivery_stop'].get('longitude'),
                        stop_type=data['delivery_stop'].get('stop_type', 'delivery'),
                        contact_name=data['delivery_stop'].get('contact_name', ''),
                        contact_phone=data['delivery_stop'].get('contact_phone', ''),
                        notes=data['delivery_stop'].get('notes', '')
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
            pickup_stops = [s for s in stops if s.stop_type == 'pickup']
            delivery_stops = [s for s in stops if s.stop_type == 'delivery']

            return JsonResponse({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
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
