import json
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import AuthToken
from .models import Order, Stop


class OrderAPITestCase(TestCase):
    def setUp(self):
        # Create test user and auth token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass'
        )
        self.auth_token = AuthToken.objects.create(user=self.user)

        # Create test order with stops
        self.order = Order.objects.create(
            customer_name='Test Customer',
            customer_company='Test Company',
            customer_email='customer@test.com',
            customer_phone='555-0123',
            goods_description='Test goods',
            goods_weight=1000.0,
            goods_volume=5.0,
            goods_type='standard',
            status='pending'
        )

        # Create pickup stop
        self.pickup_stop = Stop.objects.create(
            order=self.order,
            name='Test Pickup Location',
            address='123 Pickup St, City, State 12345',
            latitude=40.7128,
            longitude=-74.0060,
            stop_type='pickup',
            contact_name='Pickup Contact',
            contact_phone='555-0001'
        )

        # Create delivery stop
        self.delivery_stop = Stop.objects.create(
            order=self.order,
            name='Test Delivery Location',
            address='456 Delivery Ave, City, State 67890',
            latitude=34.0522,
            longitude=-118.2437,
            stop_type='delivery',
            contact_name='Delivery Contact',
            contact_phone='555-0002'
        )

    def authenticated_request(self, method, url, **kwargs):
        """Helper method to make authenticated API requests"""
        kwargs.setdefault('HTTP_AUTHORIZATION', f'Token {self.auth_token.key}')
        return getattr(self.client, method.lower())(url, **kwargs)

    def test_get_orders_list(self):
        """Test GET /api/orders/ returns properly serialized order data"""
        response = self.authenticated_request('GET', '/api/orders/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

        order_data = data['results'][0]

        # Check basic order fields
        self.assertEqual(order_data['id'], self.order.id)
        self.assertEqual(order_data['customer_name'], 'Test Customer')
        self.assertEqual(order_data['customer_company'], 'Test Company')
        self.assertEqual(order_data['goods_description'], 'Test goods')
        self.assertEqual(order_data['status'], 'pending')

        # Check stops array
        self.assertIn('stops', order_data)
        self.assertEqual(len(order_data['stops']), 2)

        # Check pickup_stop is properly serialized (not raw object)
        self.assertIn('pickup_stop', order_data)
        pickup = order_data['pickup_stop']
        self.assertIsInstance(pickup, dict)  # Should be dict, not object
        self.assertEqual(pickup['id'], self.pickup_stop.id)
        self.assertEqual(pickup['name'], 'Test Pickup Location')
        self.assertEqual(pickup['stop_type'], 'pickup')

        # Check delivery_stop is properly serialized (not raw object)
        self.assertIn('delivery_stop', order_data)
        delivery = order_data['delivery_stop']
        self.assertIsInstance(delivery, dict)  # Should be dict, not object
        self.assertEqual(delivery['id'], self.delivery_stop.id)
        self.assertEqual(delivery['name'], 'Test Delivery Location')
        self.assertEqual(delivery['stop_type'], 'delivery')

    def test_get_order_detail(self):
        """Test GET /api/orders/<id>/ returns properly serialized order data"""
        response = self.authenticated_request('GET', f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, 200)

        order_data = response.json()

        # Check basic order fields
        self.assertEqual(order_data['id'], self.order.id)
        self.assertEqual(order_data['customer_name'], 'Test Customer')

        # Check pickup_stop is properly serialized (not raw object)
        self.assertIn('pickup_stop', order_data)
        pickup = order_data['pickup_stop']
        self.assertIsInstance(pickup, dict)  # Should be dict, not object
        self.assertEqual(pickup['name'], 'Test Pickup Location')

        # Check delivery_stop is properly serialized (not raw object)
        self.assertIn('delivery_stop', order_data)
        delivery = order_data['delivery_stop']
        self.assertIsInstance(delivery, dict)  # Should be dict, not object
        self.assertEqual(delivery['name'], 'Test Delivery Location')

    def test_create_order_with_stops(self):
        """Test creating an order with stops"""
        order_data = {
            'customer_name': 'New Customer',
            'customer_company': 'New Company',
            'goods_description': 'New goods',
            'stops': [
                {
                    'name': 'New Pickup',
                    'address': '789 New St, City, State 11111',
                    'stop_type': 'pickup',
                    'contact_name': 'New Contact'
                },
                {
                    'name': 'New Delivery',
                    'address': '101 New Ave, City, State 22222',
                    'stop_type': 'delivery',
                    'contact_name': 'New Delivery Contact'
                }
            ]
        }

        response = self.authenticated_request('POST', '/api/orders/',
            data=json.dumps(order_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)

        response_data = response.json()
        self.assertEqual(response_data['customer_name'], 'New Customer')
        self.assertIn('stops', response_data)
        self.assertEqual(len(response_data['stops']), 2)

        # Verify stops were created in database
        new_order = Order.objects.get(id=response_data['id'])
        self.assertEqual(new_order.stops.count(), 2)

    def test_order_without_stops(self):
        """Test that orders without stops don't cause JSON serialization errors"""
        # Create order without stops
        empty_order = Order.objects.create(
            customer_name='Empty Customer',
            goods_description='No stops',
            status='pending'
        )

        response = self.authenticated_request('GET', '/api/orders/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # Should find both orders (original + empty)
        self.assertEqual(len(data['results']), 2)

        # Find the empty order in results
        empty_order_data = next(order for order in data['results'] if order['id'] == empty_order.id)

        # Should handle null pickup/delivery stops gracefully
        self.assertIsNone(empty_order_data['pickup_stop'])
        self.assertIsNone(empty_order_data['delivery_stop'])
        self.assertEqual(len(empty_order_data['stops']), 0)
