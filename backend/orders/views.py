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
        orders = Order.objects.select_related('pickup_stop', 'delivery_stop').all()
        data = []
        for order in orders:
            data.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'pickup_stop': {
                    'id': order.pickup_stop.id,
                    'name': order.pickup_stop.name,
                    'address': order.pickup_stop.address,
                    'latitude': str(order.pickup_stop.latitude) if order.pickup_stop.latitude else None,
                    'longitude': str(order.pickup_stop.longitude) if order.pickup_stop.longitude else None,
                    'stop_type': order.pickup_stop.stop_type,
                },
                'delivery_stop': {
                    'id': order.delivery_stop.id,
                    'name': order.delivery_stop.name,
                    'address': order.delivery_stop.address,
                    'latitude': str(order.delivery_stop.latitude) if order.delivery_stop.latitude else None,
                    'longitude': str(order.delivery_stop.longitude) if order.delivery_stop.longitude else None,
                    'stop_type': order.delivery_stop.stop_type,
                },
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
                pickup_stop_id=data['pickup_stop'],
                delivery_stop_id=data['delivery_stop'],
                goods_description=data['goods_description'],
                goods_weight=data.get('goods_weight'),
                goods_volume=data.get('goods_volume'),
                goods_type=data.get('goods_type', 'standard'),
                special_instructions=data.get('special_instructions', ''),
                requested_pickup_date=data.get('requested_pickup_date'),
                requested_delivery_date=data.get('requested_delivery_date')
            )
            order.refresh_from_db()

            return JsonResponse({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'pickup_stop': order.pickup_stop.id,
                'delivery_stop': order.delivery_stop.id,
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
            return Order.objects.select_related('pickup_stop', 'delivery_stop').get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)

        return JsonResponse({
            'id': order.id,
            'order_number': order.order_number,
            'customer_name': order.customer_name,
            'customer_company': order.customer_company,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
            'pickup_stop': {
                'id': order.pickup_stop.id,
                'name': order.pickup_stop.name,
                'address': order.pickup_stop.address,
                'latitude': str(order.pickup_stop.latitude) if order.pickup_stop.latitude else None,
                'longitude': str(order.pickup_stop.longitude) if order.pickup_stop.longitude else None,
                'stop_type': order.pickup_stop.stop_type,
            },
            'delivery_stop': {
                'id': order.delivery_stop.id,
                'name': order.delivery_stop.name,
                'address': order.delivery_stop.address,
                'latitude': str(order.delivery_stop.latitude) if order.delivery_stop.latitude else None,
                'longitude': str(order.delivery_stop.longitude) if order.delivery_stop.longitude else None,
                'stop_type': order.delivery_stop.stop_type,
            },
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

            if 'pickup_stop' in data:
                order.pickup_stop_id = data['pickup_stop']
            if 'delivery_stop' in data:
                order.delivery_stop_id = data['delivery_stop']

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

            return JsonResponse({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'customer_company': order.customer_company,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'pickup_stop': order.pickup_stop.id,
                'delivery_stop': order.delivery_stop.id,
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

            # Get existing stops
            loading_stops = list(Stop.objects.filter(stop_type='loading'))
            unloading_stops = list(Stop.objects.filter(stop_type='unloading'))

            if not loading_stops or not unloading_stops:
                return JsonResponse({'error': 'Need both loading and unloading stops to create orders'}, status=400)

            # Generate 2-5 random orders
            num_orders = random.randint(2, 5)
            created_orders = []

            for i in range(num_orders):
                pickup_stop = random.choice(loading_stops)
                delivery_stop = random.choice(unloading_stops)

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
                    pickup_stop=pickup_stop,
                    delivery_stop=delivery_stop,
                    goods_description=random.choice(goods_descriptions),
                    goods_weight=random.uniform(50, 5000),  # 50kg to 5 tons
                    goods_volume=random.uniform(1, 50),     # 1 to 50 m³
                    goods_type=random.choice(goods_types),
                    special_instructions=fake.sentence() if random.choice([True, False]) else "",
                    status='pending'
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
