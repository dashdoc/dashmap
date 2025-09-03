from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import json
from companies.models import Company
from vehicles.models import Vehicle
from .models import Position
from test_utils import AuthenticatedTestMixin

class PositionAPITestCase(TestCase, AuthenticatedTestMixin):
    def setUp(self):
        self.setUp_auth()
        self.company = Company.objects.create(
            name='Test Company',
            address='123 Test St',
            phone='555-0123',
            email='test@company.com'
        )

        self.vehicle = Vehicle.objects.create(
            company=self.company,
            license_plate='TEST-123',
            make='Ford',
            model='Transit',
            year=2023,
            capacity=2.5,
            driver_name='John Doe',
            driver_email='john@example.com',
            driver_phone='555-1234',
            is_active=True
        )

        self.position_data = {
            'vehicle_id': self.vehicle.id,
            'latitude': 40.7589123,
            'longitude': -73.9851456,
            'speed': 65.5,
            'heading': 180.0,
            'altitude': 150.25,
            'timestamp': '2024-01-15T14:30:00Z',
            'odometer': 25847.50,
            'fuel_level': 75.30,
            'engine_status': 'on'
        }

        # Create a test position
        self.position = Position.objects.create(
            vehicle=self.vehicle,
            latitude=40.7589,
            longitude=-73.9851,
            speed=60.0,
            heading=90.0,
            altitude=100.0,
            timestamp=timezone.now(),
            odometer=25000.0,
            fuel_level=80.0,
            engine_status='on'
        )

    def test_get_positions_list(self):
        response = self.authenticated_request('GET', '/api/positions/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

        position = data['results'][0]
        self.assertEqual(position['vehicle_id'], self.vehicle.id)
        self.assertEqual(position['vehicle_license_plate'], 'TEST-123')
        self.assertEqual(position['latitude'], '40.7589000')
        self.assertEqual(position['longitude'], '-73.9851000')

    def test_get_positions_filtered_by_vehicle(self):
        # Create another vehicle and position
        other_vehicle = Vehicle.objects.create(
            company=self.company,
            license_plate='OTHER-456',
            make='Toyota',
            model='Hiace',
            year=2022,
            capacity=1.5,
            driver_name='Jane Smith',
            driver_email='jane@example.com',
            is_active=True
        )

        Position.objects.create(
            vehicle=other_vehicle,
            latitude=41.8781,
            longitude=-87.6298,
            speed=45.0,
            heading=270.0,
            timestamp=timezone.now(),
            engine_status='idle'
        )

        # Filter by our original vehicle
        response = self.authenticated_request('GET', f'/api/positions/?vehicle={self.vehicle.id}')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['vehicle_id'], self.vehicle.id)

    def test_create_position(self):
        response = self.authenticated_request('POST', '/api/positions/',
                                            data=json.dumps(self.position_data),
                                            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data['vehicle_id'], self.vehicle.id)
        self.assertEqual(data['latitude'], '40.7589123')
        self.assertEqual(data['longitude'], '-73.9851456')
        self.assertEqual(data['speed'], '65.50')
        self.assertEqual(data['heading'], '180.00')
        self.assertEqual(data['altitude'], '150.25')
        self.assertEqual(data['engine_status'], 'on')

        # Verify position was created in database
        self.assertEqual(Position.objects.count(), 2)
        new_position = Position.objects.get(id=data['id'])
        self.assertEqual(new_position.vehicle.id, self.vehicle.id)
        self.assertEqual(float(new_position.latitude), 40.7589123)

    def test_create_position_minimal_data(self):
        minimal_data = {
            'vehicle_id': self.vehicle.id,
            'latitude': 42.3601,
            'longitude': -71.0589,
            'speed': 30.0,
            'heading': 45.0
        }

        response = self.authenticated_request('POST', '/api/positions/',
                                            data=json.dumps(minimal_data),
                                            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data['vehicle_id'], self.vehicle.id)
        self.assertEqual(data['engine_status'], 'off')  # default value
        self.assertIsNone(data['altitude'])
        self.assertIsNone(data['fuel_level'])

    def test_create_position_invalid_vehicle(self):
        invalid_data = self.position_data.copy()
        invalid_data['vehicle_id'] = 99999  # Non-existent vehicle

        response = self.authenticated_request('POST', '/api/positions/',
                                            data=json.dumps(invalid_data),
                                            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_position_missing_required_fields(self):
        invalid_data = {
            'vehicle_id': self.vehicle.id,
            'latitude': 40.7589
            # Missing required fields: longitude, speed, heading
        }

        response = self.authenticated_request('POST', '/api/positions/',
                                            data=json.dumps(invalid_data),
                                            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_orders(self):
        fake_data = {
            'vehicle_id': self.vehicle.id,
            'count': 5,
            'base_latitude': 34.0522,
            'base_longitude': -118.2437
        }

        initial_count = Position.objects.count()

        response = self.authenticated_request('POST', '/api/positions/generate-fake/',
                                            data=json.dumps(fake_data),
                                            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data['count'], 5)
        self.assertEqual(data['vehicle_id'], self.vehicle.id)
        self.assertIn('Generated 5 fake positions', data['message'])

        # Verify positions were created
        self.assertEqual(Position.objects.count(), initial_count + 5)

        # Check that positions are near the base coordinates
        new_positions = Position.objects.filter(vehicle=self.vehicle).exclude(id=self.position.id)
        for pos in new_positions:
            # Should be within ~5km of base coordinates (0.05 degree offset)
            self.assertAlmostEqual(float(pos.latitude), 34.0522, delta=0.06)
            self.assertAlmostEqual(float(pos.longitude), -118.2437, delta=0.06)

    def test_get_orders_default_count(self):
        fake_data = {
            'vehicle_id': self.vehicle.id
        }

        initial_count = Position.objects.count()

        response = self.authenticated_request('POST', '/api/positions/generate-fake/',
                                            data=json.dumps(fake_data),
                                            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # Default count is 10
        self.assertEqual(Position.objects.count(), initial_count + 10)

    def test_get_orders_invalid_vehicle(self):
        fake_data = {
            'vehicle_id': 99999,  # Non-existent vehicle
            'count': 3
        }

        response = self.authenticated_request('POST', '/api/positions/generate-fake/',
                                            data=json.dumps(fake_data),
                                            content_type='application/json')
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertEqual(data['error'], 'Vehicle not found')

    def test_positions_ordered_by_timestamp_desc(self):
        # Create positions with different timestamps
        now = timezone.now()

        Position.objects.create(
            vehicle=self.vehicle,
            latitude=40.7580,
            longitude=-73.9850,
            speed=50.0,
            heading=0.0,
            timestamp=now - timedelta(hours=2),
            engine_status='on'
        )

        Position.objects.create(
            vehicle=self.vehicle,
            latitude=40.7590,
            longitude=-73.9852,
            speed=55.0,
            heading=90.0,
            timestamp=now - timedelta(hours=1),
            engine_status='on'
        )

        response = self.authenticated_request('GET', '/api/positions/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        positions = data['results']

        # Should be ordered by timestamp descending (newest first)
        self.assertTrue(len(positions) >= 3)

        # Parse timestamps and verify ordering
        timestamps = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) for p in positions]
        for i in range(len(timestamps) - 1):
            self.assertGreaterEqual(timestamps[i], timestamps[i + 1])

    def test_position_model_str_method(self):
        self.assertEqual(str(self.position), f"TEST-123 - {self.position.timestamp}")

    def test_position_indexes_created(self):
        # This test verifies that the database indexes are properly created
        from django.db import connection

        with connection.cursor() as cursor:
            # Get table info to check if indexes exist
            cursor.execute("PRAGMA index_list('positions_position');")
            indexes = cursor.fetchall()

            # Should have indexes (exact names may vary by Django version)
            self.assertTrue(len(indexes) > 2)  # At least primary key + our custom indexes
