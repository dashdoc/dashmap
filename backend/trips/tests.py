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


class TripStopOrderConstraintTestCase(TripsAPITestCase):
    def setUp(self):
        super().setUp()
        # Create additional stops for testing
        self.stop3 = Stop.objects.create(
            name='Middle Stop',
            address='300 Middle Ave',
            latitude=39.9526,
            longitude=-75.1652,
            stop_type='unloading',
            contact_name='Middle Contact',
            contact_phone='555-0003'
        )

        # Create a trip with multiple ordered stops
        self.trip_stop2 = TripStop.objects.create(
            trip=self.trip,
            stop=self.stop2,
            order=2,
            planned_arrival_time=time(10, 0),
            notes='Second stop'
        )

        self.trip_stop3 = TripStop.objects.create(
            trip=self.trip,
            stop=self.stop3,
            order=3,
            planned_arrival_time=time(11, 0),
            notes='Third stop'
        )

    def test_delete_middle_stop_breaks_order_constraint(self):
        """Test that deleting a middle stop and adding a new one fails due to order constraint"""
        # Verify initial state - should have 3 stops with orders 1, 2, 3
        trip_stops = TripStop.objects.filter(trip=self.trip).order_by('order')
        self.assertEqual(trip_stops.count(), 3)
        self.assertEqual([ts.order for ts in trip_stops], [1, 2, 3])

        # Delete the middle stop (order=2)
        response = self.authenticated_request('DELETE', f'/api/trip-stops/{self.trip_stop2.id}/')
        self.assertEqual(response.status_code, 204)

        # Verify deletion
        self.assertFalse(TripStop.objects.filter(id=self.trip_stop2.id).exists())

        # Now we have stops with orders [1, 3], but trying to add order=2 should work
        # This currently fails due to the unique constraint bug
        new_stop = Stop.objects.create(
            name='New Middle Stop',
            address='250 New Middle St',
            stop_type='loading'
        )

        new_trip_stop_data = {
            'trip': self.trip.id,
            'stop': new_stop.id,
            'order': 2,  # This should be valid since order=2 was deleted
            'planned_arrival_time': '10:30:00',
            'notes': 'New middle stop'
        }

        # After the fix, this should work without any issues
        response = self.authenticated_request('POST',
            '/api/trip-stops/',
            data=json.dumps(new_trip_stop_data),
            content_type='application/json'
        )

        # Should succeed now that the bug is fixed
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['order'], 2)

        # Verify the trip now has the expected stops in order
        trip_stops = TripStop.objects.filter(trip=self.trip).order_by('order')
        orders = [ts.order for ts in trip_stops]
        # Should have orders [1, 2, 3] where order 2 is the new stop and order 3 remained unchanged
        self.assertEqual(orders, [1, 2, 3])

    def test_delete_last_stop_and_add_multiple_stops(self):
        """Test deleting the last stop and adding multiple new stops"""
        # Delete the last stop (order=3)
        response = self.authenticated_request('DELETE', f'/api/trip-stops/{self.trip_stop3.id}/')
        self.assertEqual(response.status_code, 204)

        # Try to add two new stops with orders 3 and 4
        new_stop1 = Stop.objects.create(name='New Stop 1', address='400 New St', stop_type='loading')
        new_stop2 = Stop.objects.create(name='New Stop 2', address='500 New St', stop_type='unloading')

        # Add first new stop
        response1 = self.authenticated_request('POST', '/api/trip-stops/',
            data=json.dumps({
                'trip': self.trip.id,
                'stop': new_stop1.id,
                'order': 3,
                'planned_arrival_time': '11:00:00'
            }),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 201)

        # Add second new stop
        response2 = self.authenticated_request('POST', '/api/trip-stops/',
            data=json.dumps({
                'trip': self.trip.id,
                'stop': new_stop2.id,
                'order': 4,
                'planned_arrival_time': '12:00:00'
            }),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 201)

    def test_order_constraint_with_gaps(self):
        """Test that order constraint allows gaps in ordering"""
        # Delete middle stop to create gap
        self.trip_stop2.delete()

        # Should be able to create stops with orders that skip numbers
        new_stop = Stop.objects.create(name='Skip Order Stop', address='600 Skip St', stop_type='loading')

        response = self.authenticated_request('POST', '/api/trip-stops/',
            data=json.dumps({
                'trip': self.trip.id,
                'stop': new_stop.id,
                'order': 5,  # Skip order 4
                'planned_arrival_time': '13:00:00'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        # Verify final order sequence
        trip_stops = TripStop.objects.filter(trip=self.trip).order_by('order')
        orders = [ts.order for ts in trip_stops]
        self.assertEqual(orders, [1, 3, 5])  # Should have gaps

    def test_duplicate_order_constraint(self):
        """Test that duplicate orders are properly handled by shifting existing stops"""
        new_stop = Stop.objects.create(name='Duplicate Order Stop', address='700 Dup St', stop_type='loading')

        # Verify initial state - should have 3 stops with orders 1, 2, 3
        initial_stops = TripStop.objects.filter(trip=self.trip).order_by('order')
        initial_orders = [ts.order for ts in initial_stops]
        self.assertEqual(initial_orders, [1, 2, 3])

        # Try to create a stop with order=1 (already exists)
        response = self.authenticated_request('POST', '/api/trip-stops/',
            data=json.dumps({
                'trip': self.trip.id,
                'stop': new_stop.id,
                'order': 1,  # This order already exists
                'planned_arrival_time': '08:30:00'
            }),
            content_type='application/json'
        )

        # After fix, this should succeed by shifting existing stops
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['order'], 1)  # New stop should get the requested order

        # Verify that existing stops were shifted
        all_stops = TripStop.objects.filter(trip=self.trip).order_by('order')
        final_orders = [ts.order for ts in all_stops]
        # Should now have orders [1, 2, 3, 4] where the new stop is at order 1
        # and the original stops are shifted to 2, 3, 4
        self.assertEqual(final_orders, [1, 2, 3, 4])
        self.assertEqual(all_stops.count(), 4)

        # Verify the new stop is at order 1
        new_trip_stop = TripStop.objects.get(id=data['id'])
        self.assertEqual(new_trip_stop.order, 1)
        self.assertEqual(new_trip_stop.stop, new_stop)
