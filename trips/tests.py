from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
import json
from datetime import date, time
from companies.models import Company
from vehicles.models import Vehicle
from .models import Stop, Trip, TripStop
from test_utils import AuthenticatedTestMixin

class TripsAPITestCase(TestCase, AuthenticatedTestMixin):
    def setUp(self):
        self.setUp_auth()
        # Create test data
        self.company = Company.objects.create(
            name='Test Company',
            address='123 Test St'
        )
        
        self.user = User.objects.create_user(
            username='dispatcher',
            email='dispatcher@test.com',
            first_name='John',
            last_name='Dispatcher'
        )
        
        self.vehicle = Vehicle.objects.create(
            company=self.company,
            license_plate='ABC123',
            make='Ford',
            model='Transit',
            year=2023,
            capacity=2.5,
            driver_name='Driver Joe',
            driver_email='driver@test.com',
            driver_phone='555-1234'
        )
        
        self.stop1 = Stop.objects.create(
            name='Loading Dock A',
            address='100 Warehouse St',
            stop_type='loading',
            contact_name='Loading Manager',
            contact_phone='555-0001'
        )
        
        self.stop2 = Stop.objects.create(
            name='Customer Site B',
            address='200 Customer Ave',
            stop_type='unloading',
            contact_name='Customer Rep',
            contact_phone='555-0002'
        )
        
        self.trip = Trip.objects.create(
            vehicle=self.vehicle,
            dispatcher=self.user,
            name='Test Trip',
            status='draft',
            planned_start_date=date(2024, 1, 15),
            planned_start_time=time(8, 0),
            notes='Test trip notes'
        )
        
        self.trip_stop = TripStop.objects.create(
            trip=self.trip,
            stop=self.stop1,
            order=1,
            planned_arrival_time=time(9, 0),
            notes='First stop notes'
        )

class StopAPITestCase(TripsAPITestCase):
    def test_get_stops_list(self):
        response = self.authenticated_request('GET', '/api/stops/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)
        
    def test_create_stop(self):
        new_stop_data = {
            'name': 'New Stop',
            'address': '300 New St',
            'stop_type': 'loading',
            'contact_name': 'Contact Person',
            'contact_phone': '555-9999'
        }
        
        response = self.authenticated_request('POST', 
            '/api/stops/',
            data=json.dumps(new_stop_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'New Stop')
        self.assertEqual(data['stop_type'], 'loading')
        
    def test_update_stop(self):
        updated_data = {
            'contact_name': 'Updated Contact'
        }
        
        response = self.authenticated_request('PUT', 
            f'/api/stops/{self.stop1.id}/',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['contact_name'], 'Updated Contact')

class TripAPITestCase(TripsAPITestCase):
    def test_get_trips_list(self):
        response = self.authenticated_request('GET', '/api/trips/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        
        trip_data = data['results'][0]
        self.assertEqual(trip_data['name'], 'Test Trip')
        self.assertEqual(trip_data['vehicle_license_plate'], 'ABC123')
        
    def test_filter_trips_by_vehicle(self):
        response = self.authenticated_request('GET', f'/api/trips/?vehicle={self.vehicle.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['vehicle'], self.vehicle.id)
        
    def test_filter_trips_by_company(self):
        response = self.authenticated_request('GET', f'/api/trips/?company={self.company.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        
    def test_create_trip(self):
        new_trip_data = {
            'vehicle': self.vehicle.id,
            'dispatcher': self.user.id,
            'name': 'New Trip',
            'status': 'draft',
            'planned_start_date': '2024-01-20',
            'planned_start_time': '10:00:00',
            'notes': 'New trip notes'
        }
        
        response = self.authenticated_request('POST', 
            '/api/trips/',
            data=json.dumps(new_trip_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'New Trip')
        self.assertEqual(data['status'], 'draft')
        
    def test_get_trip_detail_with_stops(self):
        response = self.authenticated_request('GET', f'/api/trips/{self.trip.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['name'], 'Test Trip')
        self.assertIn('trip_stops', data)
        self.assertEqual(len(data['trip_stops']), 1)
        
        trip_stop_data = data['trip_stops'][0]
        self.assertEqual(trip_stop_data['order'], 1)
        self.assertEqual(trip_stop_data['stop']['name'], 'Loading Dock A')
        
    def test_update_trip(self):
        updated_data = {
            'status': 'planned',
            'notes': 'Updated trip notes'
        }
        
        response = self.authenticated_request('PUT', 
            f'/api/trips/{self.trip.id}/',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'planned')
        self.assertEqual(data['notes'], 'Updated trip notes')
        
    def test_notify_driver(self):
        response = self.authenticated_request('POST', f'/api/trips/{self.trip.id}/notify-driver/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('successfully', data['message'])
        
        # Check that email was sent (to console in test)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Trip Assignment', mail.outbox[0].subject)
        self.assertIn('Driver Joe', mail.outbox[0].body)
        
        # Check that trip was marked as notified
        self.trip.refresh_from_db()
        self.assertTrue(self.trip.driver_notified)
        
    def test_notify_driver_already_notified(self):
        # Mark trip as already notified
        self.trip.driver_notified = True
        self.trip.save()
        
        response = self.authenticated_request('POST', f'/api/trips/{self.trip.id}/notify-driver/')
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('already notified', data['message'])

class TripStopAPITestCase(TripsAPITestCase):
    def test_get_trip_stops_list(self):
        response = self.authenticated_request('GET', '/api/trip-stops/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        
    def test_filter_trip_stops_by_trip(self):
        response = self.authenticated_request('GET', f'/api/trip-stops/?trip={self.trip.id}')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['trip'], self.trip.id)
        
    def test_create_trip_stop(self):
        new_trip_stop_data = {
            'trip': self.trip.id,
            'stop': self.stop2.id,
            'order': 2,
            'planned_arrival_time': '11:00:00',
            'notes': 'Second stop notes'
        }
        
        response = self.authenticated_request('POST', 
            '/api/trip-stops/',
            data=json.dumps(new_trip_stop_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['order'], 2)
        self.assertEqual(data['stop']['name'], 'Customer Site B')
        
    def test_update_trip_stop(self):
        updated_data = {
            'is_completed': True,
            'notes': 'Completed successfully'
        }
        
        response = self.authenticated_request('PUT', 
            f'/api/trip-stops/{self.trip_stop.id}/',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['is_completed'], True)
        self.assertEqual(data['notes'], 'Completed successfully')
        
    def test_delete_trip_stop(self):
        response = self.authenticated_request('DELETE', f'/api/trip-stops/{self.trip_stop.id}/')
        self.assertEqual(response.status_code, 204)
        
        # Verify deletion
        self.assertFalse(TripStop.objects.filter(id=self.trip_stop.id).exists())
