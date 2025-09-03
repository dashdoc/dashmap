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
            latitude=41.878113,
            longitude=-87.629799,
            stop_type='loading',
            contact_name='Loading Manager',
            contact_phone='555-0001'
        )

        self.stop2 = Stop.objects.create(
            name='Customer Site B',
            address='200 Customer Ave',
            latitude=40.712776,
            longitude=-74.005974,
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

        # Verify latitude and longitude are included in response
        stop_data = data['results'][0]
        self.assertIn('latitude', stop_data)
        self.assertIn('longitude', stop_data)
        self.assertIsNotNone(stop_data['latitude'])
        self.assertIsNotNone(stop_data['longitude'])

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
        # Verify coordinates fields are present (should be null)
        self.assertIn('latitude', data)
        self.assertIn('longitude', data)
        self.assertIsNone(data['latitude'])
        self.assertIsNone(data['longitude'])

    def test_create_stop_with_coordinates(self):
        new_stop_data = {
            'name': 'Coordinated Stop',
            'address': '400 GPS St',
            'latitude': 34.052235,
            'longitude': -118.243683,
            'stop_type': 'unloading',
            'contact_name': 'GPS Contact',
            'contact_phone': '555-7777'
        }

        response = self.authenticated_request('POST',
            '/api/stops/',
            data=json.dumps(new_stop_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'Coordinated Stop')
        self.assertEqual(data['latitude'], '34.052235')
        self.assertEqual(data['longitude'], '-118.243683')

        # Verify in database
        stop = Stop.objects.get(id=data['id'])
        self.assertEqual(float(stop.latitude), 34.052235)
        self.assertEqual(float(stop.longitude), -118.243683)

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
        # Verify coordinates are still included and unchanged
        self.assertIn('latitude', data)
        self.assertIn('longitude', data)
        self.assertEqual(data['latitude'], '41.878113')
        self.assertEqual(data['longitude'], '-87.629799')

    def test_update_stop_coordinates(self):
        updated_data = {
            'latitude': 42.3601,
            'longitude': -71.0589
        }

        response = self.authenticated_request('PUT',
            f'/api/stops/{self.stop1.id}/',
            data=json.dumps(updated_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['latitude'], '42.3601')  # DecimalField formatting removes trailing zeros
        self.assertEqual(data['longitude'], '-71.0589')

        # Verify in database
        self.stop1.refresh_from_db()
        self.assertEqual(float(self.stop1.latitude), 42.3601)
        self.assertEqual(float(self.stop1.longitude), -71.0589)

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

        # Verify coordinates are included in nested stop data
        stop_data = trip_stop_data['stop']
        self.assertIn('latitude', stop_data)
        self.assertIn('longitude', stop_data)
        self.assertEqual(stop_data['latitude'], '41.878113')
        self.assertEqual(stop_data['longitude'], '-87.629799')

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

        # Verify coordinates are included in trip stop stop data
        trip_stop_data = data['results'][0]
        stop_data = trip_stop_data['stop']
        self.assertIn('latitude', stop_data)
        self.assertIn('longitude', stop_data)
        self.assertEqual(stop_data['latitude'], '41.878113')
        self.assertEqual(stop_data['longitude'], '-87.629799')

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

        # Verify coordinates are included in response
        stop_data = data['stop']
        self.assertIn('latitude', stop_data)
        self.assertIn('longitude', stop_data)
        self.assertEqual(stop_data['latitude'], '40.712776')
        self.assertEqual(stop_data['longitude'], '-74.005974')

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

class GetOrdersAPITestCase(TripsAPITestCase):
    def test_get_orders_success(self):
        """Test that the get orders endpoint creates random stops successfully"""
        initial_stop_count = Stop.objects.count()

        response = self.authenticated_request('POST', '/api/stops/generate-fake/')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertIn('message', data)
        self.assertIn('created_stops', data)

        # Verify that stops were created
        new_stop_count = Stop.objects.count()
        created_count = len(data['created_stops'])
        self.assertEqual(new_stop_count, initial_stop_count + created_count)
        self.assertTrue(3 <= created_count <= 8)  # Should create 3-8 stops

        # Verify structure of created stops
        for stop_data in data['created_stops']:
            self.assertIn('id', stop_data)
            self.assertIn('name', stop_data)
            self.assertIn('address', stop_data)
            self.assertIn('latitude', stop_data)
            self.assertIn('longitude', stop_data)
            self.assertIn('stop_type', stop_data)
            self.assertIn('contact_name', stop_data)
            self.assertIn('contact_phone', stop_data)
            self.assertIn('created_at', stop_data)

            # Verify coordinates are present and valid
            self.assertIsNotNone(stop_data['latitude'])
            self.assertIsNotNone(stop_data['longitude'])

            # Verify coordinates are within valid ranges
            lat = float(stop_data['latitude'])
            lng = float(stop_data['longitude'])
            self.assertGreaterEqual(lat, -90.0)
            self.assertLessEqual(lat, 90.0)
            self.assertGreaterEqual(lng, -180.0)
            self.assertLessEqual(lng, 180.0)

            # Verify stop_type is valid
            self.assertIn(stop_data['stop_type'], ['loading', 'unloading'])

            # Verify required fields are not empty
            self.assertTrue(stop_data['name'])
            self.assertTrue(stop_data['address'])
            self.assertTrue(stop_data['contact_name'])

    def test_get_orders_creates_realistic_data(self):
        """Test that generated data is realistic"""
        response = self.authenticated_request('POST', '/api/stops/generate-fake/')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        created_stops = data['created_stops']

        # Check that we have both loading and unloading stops (with reasonable probability)
        stop_types = [stop['stop_type'] for stop in created_stops]
        # We can't guarantee both types in every run due to randomness, but verify valid types
        for stop_type in stop_types:
            self.assertIn(stop_type, ['loading', 'unloading'])

        # Verify name patterns are reasonable
        for stop in created_stops:
            if stop['stop_type'] == 'loading':
                # Loading stops should have warehouse-like names
                name_lower = stop['name'].lower()
                self.assertTrue(any(word in name_lower for word in
                    ['warehouse', 'distribution', 'loading', 'supply']))
            else:
                # Unloading stops should have store/customer-like names
                # Just verify they have some text (company names are varied)
                self.assertTrue(len(stop['name']) > 0)

        # Verify addresses have proper format (street, city, state zip)
        for stop in created_stops:
            address = stop['address']
            self.assertIn(',', address)  # Should have commas separating parts
            parts = address.split(',')
            self.assertTrue(len(parts) >= 3)  # street, city, state zip

    def test_get_orders_phone_length_constraint(self):
        """Test that phone numbers are properly truncated to fit model constraints"""
        response = self.authenticated_request('POST', '/api/stops/generate-fake/')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        for stop in data['created_stops']:
            # Phone field has max_length=20 in model, API truncates to 15
            self.assertTrue(len(stop['contact_phone']) <= 15)

    def test_get_orders_coordinates_persistence(self):
        """Test that generated coordinates are properly saved to database"""
        response = self.authenticated_request('POST', '/api/stops/generate-fake/')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        created_stops = data['created_stops']

        # Verify coordinates are saved in database
        for stop_data in created_stops:
            stop = Stop.objects.get(id=stop_data['id'])
            self.assertIsNotNone(stop.latitude)
            self.assertIsNotNone(stop.longitude)

            # Verify API response matches database values (allowing for DecimalField precision)
            db_lat = float(str(stop.latitude))
            db_lng = float(str(stop.longitude))
            api_lat = float(stop_data['latitude'])
            api_lng = float(stop_data['longitude'])

            # Allow for minor precision differences due to DecimalField rounding
            self.assertAlmostEqual(db_lat, api_lat, places=5)
            self.assertAlmostEqual(db_lng, api_lng, places=5)

    def test_get_orders_coordinate_precision(self):
        """Test that coordinates are valid decimal numbers"""
        response = self.authenticated_request('POST', '/api/stops/generate-fake/')
        self.assertEqual(response.status_code, 201)

        data = response.json()
        for stop_data in data['created_stops']:
            # Verify coordinates are valid decimal numbers
            lat_str = stop_data['latitude']
            lng_str = stop_data['longitude']

            # Should be able to convert to float
            lat = float(lat_str)
            lng = float(lng_str)

            # Should be valid coordinate ranges
            self.assertGreaterEqual(lat, -90.0)
            self.assertLessEqual(lat, 90.0)
            self.assertGreaterEqual(lng, -180.0)
            self.assertLessEqual(lng, 180.0)

            # Verify the values can round-trip through the database
            stop = Stop.objects.get(id=stop_data['id'])
            self.assertAlmostEqual(float(str(stop.latitude)), lat, places=5)
            self.assertAlmostEqual(float(str(stop.longitude)), lng, places=5)
