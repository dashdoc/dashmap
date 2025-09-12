from django.test import TestCase
from django.contrib.auth.models import User
import json
from companies.models import Company
from .models import Vehicle
from test_utils import AuthenticatedTestMixin

class VehicleAPITestCase(TestCase, AuthenticatedTestMixin):
    def setUp(self):
        self.setUp_auth()
        self.company = Company.objects.create(
            name='Test Company',
            address='123 Test St',
            phone='555-0123',
            email='test@company.com'
        )

        self.vehicle_data = {
            'company': self.company.id,
            'license_plate': 'ABC123',
            'make': 'Ford',
            'model': 'Transit',
            'year': 2023,
            'capacity': 2.5,
            'driver_name': 'John Doe',
            'driver_email': 'john@example.com',
            'driver_phone': '555-1234',
            'is_active': True
        }

        self.vehicle = Vehicle.objects.create(
            company=self.company,
            license_plate='ABC123',
            make='Ford',
            model='Transit',
            year=2023,
            capacity=2.5,
            driver_name='John Doe',
            driver_email='john@example.com',
            driver_phone='555-1234',
            is_active=True
        )

    def test_get_vehicles_list(self):
        response = self.authenticated_request('GET', '/api/vehicles/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

        vehicle_data = data['results'][0]
        self.assertEqual(vehicle_data['license_plate'], 'ABC123')
        self.assertEqual(vehicle_data['company_name'], 'Test Company')

    def test_filter_vehicles_by_company(self):
        # Create another company and vehicle
        company2 = Company.objects.create(name='Company 2', address='456 St')
        Vehicle.objects.create(
            company=company2,
            license_plate='XYZ789',
            make='Chevrolet',
            model='Express',
            year=2022,
            capacity=3.0,
            driver_name='Jane Smith',
            driver_email='jane@example.com'
        )

        response = self.authenticated_request('GET', f'/api/vehicles/?company={self.company.id}')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['license_plate'], 'ABC123')

    def test_create_vehicle(self):
        new_vehicle_data = {
            'company': self.company.id,
            'license_plate': 'NEW123',
            'make': 'Mercedes',
            'model': 'Sprinter',
            'year': 2024,
            'capacity': 3.5,
            'driver_name': 'Bob Wilson',
            'driver_email': 'bob@example.com',
            'driver_phone': '555-5678'
        }

        response = self.authenticated_request(
            'POST',
            '/api/vehicles/',
            data=json.dumps(new_vehicle_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['license_plate'], 'NEW123')
        self.assertEqual(data['driver_name'], 'Bob Wilson')

        # Verify vehicle was created in database
        self.assertTrue(Vehicle.objects.filter(license_plate='NEW123').exists())

    def test_get_vehicle_detail(self):
        response = self.authenticated_request('GET', f'/api/vehicles/{self.vehicle.id}/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['license_plate'], 'ABC123')
        self.assertEqual(data['driver_name'], 'John Doe')
        self.assertEqual(data['company_name'], 'Test Company')

    def test_update_vehicle(self):
        updated_data = {
            'driver_name': 'Johnny Doe',
            'capacity': 3.0
        }

        response = self.authenticated_request(
            'PUT',
            f'/api/vehicles/{self.vehicle.id}/',
            data=json.dumps(updated_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['driver_name'], 'Johnny Doe')
        self.assertEqual(data['capacity'], '3.0')

        # Verify update in database
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.driver_name, 'Johnny Doe')

    def test_delete_vehicle(self):
        response = self.authenticated_request('DELETE', f'/api/vehicles/{self.vehicle.id}/')
        self.assertEqual(response.status_code, 204)

        # Verify soft deletion - vehicle should have deleted_at timestamp set
        self.vehicle.refresh_from_db()
        self.assertIsNotNone(self.vehicle.deleted_at)

    def test_get_nonexistent_vehicle(self):
        response = self.authenticated_request('GET', '/api/vehicles/999/')
        self.assertEqual(response.status_code, 404)

    def test_create_vehicle_invalid_data(self):
        invalid_data = {'license_plate': ''}  # Missing required fields

        response = self.authenticated_request(
            'POST',
            '/api/vehicles/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
