from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
import json
from datetime import date, time
from companies.models import Company
from vehicles.models import Vehicle
from .models import Trip, TripStop
from .services import (
    validate_trip_stops_completeness,
    validate_new_trip_stop,
    get_incomplete_orders,
    ensure_order_pair_in_trip,
    add_order_to_trip,
    validate_pickup_before_delivery,
    TripValidationError
)
from orders.models import Stop, Order
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

    def test_post_trip_stop_not_allowed(self):
        """Test that POST to trip-stops endpoint is no longer allowed"""
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

        # POST should return 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)

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




class TripValidationServiceTestCase(TestCase):
    """Test cases for the trip validation service functions"""

    def setUp(self):
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

        self.trip = Trip.objects.create(
            vehicle=self.vehicle,
            dispatcher=self.user,
            name='Test Trip',
            status='draft',
            planned_start_date=date.today(),
            planned_start_time=time(9, 0)
        )

        # Create a complete order with pickup and delivery stops
        self.order = Order.objects.create(
            customer_name='Test Customer',
            customer_company='Test Corp',
            customer_email='customer@test.com',
            goods_description='Test goods',
            goods_weight=100.0,
            goods_volume=5.0
        )

        self.pickup_stop = Stop.objects.create(
            order=self.order,
            name='Pickup Location',
            address='100 Pickup St',
            stop_type='pickup',
            contact_name='Pickup Contact'
        )

        self.delivery_stop = Stop.objects.create(
            order=self.order,
            name='Delivery Location',
            address='200 Delivery Ave',
            stop_type='delivery',
            contact_name='Delivery Contact'
        )

        # Create an incomplete order (only pickup)
        self.incomplete_order = Order.objects.create(
            customer_name='Incomplete Customer',
            customer_company='Incomplete Corp',
            goods_description='Incomplete goods'
        )

        self.incomplete_pickup = Stop.objects.create(
            order=self.incomplete_order,
            name='Incomplete Pickup',
            address='300 Incomplete St',
            stop_type='pickup',
            contact_name='Incomplete Contact'
        )

    def test_validate_new_trip_stop_success_with_paired_stop_in_trip(self):
        """Test that validation passes when paired stop is already in the trip"""
        # Add pickup stop to trip first (skip validation for test setup)
        pickup_trip_stop = TripStop(
            trip=self.trip,
            stop=self.pickup_stop,
            order=1,
            planned_arrival_time=time(10, 0)
        )
        pickup_trip_stop.save(skip_validation=True)

        # Adding delivery stop should succeed since pickup is already in trip
        try:
            validate_new_trip_stop(self.trip, self.delivery_stop)
        except TripValidationError:
            self.fail("validate_new_trip_stop raised TripValidationError unexpectedly")

    def test_validate_new_trip_stop_fails_without_paired_stop(self):
        """Test that validation fails when paired stop is not in the trip"""
        # Try to add delivery stop without pickup stop in trip
        with self.assertRaises(TripValidationError) as context:
            validate_new_trip_stop(self.trip, self.delivery_stop)

        self.assertIn("without also including its pickup stop", str(context.exception))

    def test_validate_new_trip_stop_allows_stops_without_orders(self):
        """Test that stops without orders are allowed"""
        # Create a stop without an order
        standalone_stop = Stop.objects.create(
            name='Standalone Stop',
            address='400 Standalone St',
            stop_type='pickup',
            contact_name='Standalone Contact'
        )

        # Should not raise an exception
        try:
            validate_new_trip_stop(self.trip, standalone_stop)
        except TripValidationError:
            self.fail("validate_new_trip_stop should allow stops without orders")

    def test_validate_new_trip_stop_fails_incomplete_order(self):
        """Test that validation fails for orders without paired stops"""
        with self.assertRaises(TripValidationError) as context:
            validate_new_trip_stop(self.trip, self.incomplete_pickup)

        self.assertIn("does not have a delivery stop", str(context.exception))

    def test_get_incomplete_orders_empty_trip(self):
        """Test get_incomplete_orders returns empty list for trip without stops"""
        incomplete = get_incomplete_orders(self.trip)
        self.assertEqual(len(incomplete), 0)

    def test_get_incomplete_orders_with_complete_order(self):
        """Test get_incomplete_orders when trip has complete orders"""
        # Add complete order to trip
        add_order_to_trip(
            trip=self.trip,
            order=self.order,
            pickup_time=time(10, 0),
            delivery_time=time(11, 0)
        )

        incomplete = get_incomplete_orders(self.trip)
        self.assertEqual(len(incomplete), 0)

    def test_get_incomplete_orders_with_incomplete_order(self):
        """Test get_incomplete_orders when trip has incomplete orders"""
        # Add only pickup stop (skip validation for test setup)
        pickup_trip_stop = TripStop(
            trip=self.trip,
            stop=self.pickup_stop,
            order=1,
            planned_arrival_time=time(10, 0)
        )
        pickup_trip_stop.save(skip_validation=True)

        incomplete = get_incomplete_orders(self.trip)
        self.assertEqual(len(incomplete), 1)
        self.assertEqual(incomplete[0], self.order)

    def test_validate_trip_stops_completeness_success(self):
        """Test validate_trip_stops_completeness passes for complete trip"""
        # Add complete order to trip
        add_order_to_trip(
            trip=self.trip,
            order=self.order,
            pickup_time=time(10, 0),
            delivery_time=time(11, 0)
        )

        try:
            validate_trip_stops_completeness(self.trip)
        except TripValidationError:
            self.fail("validate_trip_stops_completeness raised TripValidationError unexpectedly")

    def test_validate_trip_stops_completeness_fails_incomplete(self):
        """Test validate_trip_stops_completeness fails for incomplete trip"""
        # Add only pickup stop (skip validation for test setup)
        pickup_trip_stop = TripStop(
            trip=self.trip,
            stop=self.pickup_stop,
            order=1,
            planned_arrival_time=time(10, 0)
        )
        pickup_trip_stop.save(skip_validation=True)

        with self.assertRaises(TripValidationError) as context:
            validate_trip_stops_completeness(self.trip)

        self.assertIn("contains incomplete orders", str(context.exception))
        self.assertIn(self.order.order_number, str(context.exception))

    def test_ensure_order_pair_in_trip_success(self):
        """Test ensure_order_pair_in_trip returns both stops for complete order"""
        result = ensure_order_pair_in_trip(self.trip, self.order)

        self.assertEqual(result['pickup_stop'], self.pickup_stop)
        self.assertEqual(result['delivery_stop'], self.delivery_stop)

    def test_ensure_order_pair_in_trip_fails_incomplete(self):
        """Test ensure_order_pair_in_trip fails for incomplete order"""
        with self.assertRaises(TripValidationError) as context:
            ensure_order_pair_in_trip(self.trip, self.incomplete_order)

        self.assertIn("does not have a delivery stop", str(context.exception))

    def test_add_order_to_trip_success(self):
        """Test add_order_to_trip successfully adds both stops"""
        result = add_order_to_trip(
            trip=self.trip,
            order=self.order,
            pickup_time=time(10, 0),
            delivery_time=time(11, 0),
            notes="Test order"
        )

        # Check that both trip stops were created
        self.assertIn('pickup_trip_stop', result)
        self.assertIn('delivery_trip_stop', result)

        pickup_ts = result['pickup_trip_stop']
        delivery_ts = result['delivery_trip_stop']

        # Verify pickup stop
        self.assertEqual(pickup_ts.trip, self.trip)
        self.assertEqual(pickup_ts.stop, self.pickup_stop)
        self.assertEqual(pickup_ts.order, 1)
        self.assertEqual(pickup_ts.planned_arrival_time, time(10, 0))

        # Verify delivery stop
        self.assertEqual(delivery_ts.trip, self.trip)
        self.assertEqual(delivery_ts.stop, self.delivery_stop)
        self.assertEqual(delivery_ts.order, 2)
        self.assertEqual(delivery_ts.planned_arrival_time, time(11, 0))

        # Verify trip now has 2 stops
        self.assertEqual(self.trip.trip_stops.count(), 2)

    def test_add_order_to_trip_fails_incomplete(self):
        """Test add_order_to_trip fails for incomplete order"""
        with self.assertRaises(TripValidationError) as context:
            add_order_to_trip(
                trip=self.trip,
                order=self.incomplete_order,
                pickup_time=time(10, 0),
                delivery_time=time(11, 0)
            )

        self.assertIn("does not have a delivery stop", str(context.exception))

    def test_validate_pickup_before_delivery_success(self):
        """Test validate_pickup_before_delivery passes when pickup comes before delivery"""
        # Add complete order with pickup before delivery
        add_order_to_trip(
            trip=self.trip,
            order=self.order,
            pickup_time=time(10, 0),
            delivery_time=time(11, 0)
        )

        # Should not raise an exception
        try:
            validate_pickup_before_delivery(self.trip)
        except TripValidationError:
            self.fail("validate_pickup_before_delivery raised TripValidationError unexpectedly")

    def test_validate_pickup_before_delivery_fails_delivery_first(self):
        """Test validate_pickup_before_delivery fails when delivery comes before pickup"""
        # Manually create trip stops with delivery before pickup (skip validation)
        delivery_trip_stop = TripStop(
            trip=self.trip,
            stop=self.delivery_stop,
            order=1,  # Delivery at position 1
            planned_arrival_time=time(10, 0)
        )
        delivery_trip_stop.save(skip_validation=True)

        pickup_trip_stop = TripStop(
            trip=self.trip,
            stop=self.pickup_stop,
            order=2,  # Pickup at position 2 (after delivery)
            planned_arrival_time=time(11, 0)
        )
        pickup_trip_stop.save(skip_validation=True)

        with self.assertRaises(TripValidationError) as context:
            validate_pickup_before_delivery(self.trip)

        self.assertIn("delivery stop (position 1) before or at same position as pickup stop (position 2)", str(context.exception))

    def test_validate_pickup_before_delivery_fails_equal_position(self):
        """Test validate_pickup_before_delivery correctly handles the >= condition"""
        # Test that delivery at position 2 and pickup at position 3 fails (delivery comes first)
        delivery_trip_stop = TripStop(
            trip=self.trip,
            stop=self.delivery_stop,
            order=1,  # Delivery at position 1
            planned_arrival_time=time(10, 0)
        )
        delivery_trip_stop.save(skip_validation=True)

        pickup_trip_stop = TripStop(
            trip=self.trip,
            stop=self.pickup_stop,
            order=2,  # Pickup at position 2 (after delivery)
            planned_arrival_time=time(11, 0)
        )
        pickup_trip_stop.save(skip_validation=True)

        with self.assertRaises(TripValidationError) as context:
            validate_pickup_before_delivery(self.trip)

        self.assertIn("delivery stop (position 1) before or at same position as pickup stop (position 2)", str(context.exception))

    def test_validate_pickup_before_delivery_multiple_orders(self):
        """Test validate_pickup_before_delivery with multiple orders"""
        # Create second complete order
        order2 = Order.objects.create(
            customer_name='Customer 2',
            customer_company='Corp 2',
            goods_description='Goods 2'
        )

        pickup_stop2 = Stop.objects.create(
            order=order2,
            name='Pickup Location 2',
            address='500 Pickup St',
            stop_type='pickup',
            contact_name='Pickup Contact 2'
        )

        delivery_stop2 = Stop.objects.create(
            order=order2,
            name='Delivery Location 2',
            address='600 Delivery Ave',
            stop_type='delivery',
            contact_name='Delivery Contact 2'
        )

        # Add both orders correctly (pickup before delivery for each)
        add_order_to_trip(
            trip=self.trip,
            order=self.order,
            pickup_time=time(10, 0),
            delivery_time=time(11, 0)
        )

        add_order_to_trip(
            trip=self.trip,
            order=order2,
            pickup_time=time(12, 0),
            delivery_time=time(13, 0)
        )

        # Should pass validation
        try:
            validate_pickup_before_delivery(self.trip)
        except TripValidationError:
            self.fail("validate_pickup_before_delivery should pass for multiple correct orders")

    def test_validate_pickup_before_delivery_mixed_correct_incorrect(self):
        """Test validate_pickup_before_delivery fails when one order is incorrect"""
        # Create second complete order
        order2 = Order.objects.create(
            customer_name='Customer 2',
            customer_company='Corp 2',
            goods_description='Goods 2'
        )

        pickup_stop2 = Stop.objects.create(
            order=order2,
            name='Pickup Location 2',
            address='500 Pickup St',
            stop_type='pickup',
            contact_name='Pickup Contact 2'
        )

        delivery_stop2 = Stop.objects.create(
            order=order2,
            name='Delivery Location 2',
            address='600 Delivery Ave',
            stop_type='delivery',
            contact_name='Delivery Contact 2'
        )

        # Add first order correctly
        add_order_to_trip(
            trip=self.trip,
            order=self.order,
            pickup_time=time(10, 0),
            delivery_time=time(11, 0)
        )

        # Add second order incorrectly (delivery before pickup) - skip validation
        delivery_trip_stop2 = TripStop(
            trip=self.trip,
            stop=delivery_stop2,
            order=3,  # Delivery at position 3
            planned_arrival_time=time(12, 0)
        )
        delivery_trip_stop2.save(skip_validation=True)

        pickup_trip_stop2 = TripStop(
            trip=self.trip,
            stop=pickup_stop2,
            order=4,  # Pickup at position 4 (after delivery)
            planned_arrival_time=time(13, 0)
        )
        pickup_trip_stop2.save(skip_validation=True)

        with self.assertRaises(TripValidationError) as context:
            validate_pickup_before_delivery(self.trip)

        self.assertIn(order2.order_number, str(context.exception))
        self.assertIn("delivery stop (position 3) before or at same position as pickup stop (position 4)", str(context.exception))

    def test_validate_pickup_before_delivery_empty_trip(self):
        """Test validate_pickup_before_delivery passes for empty trip"""
        try:
            validate_pickup_before_delivery(self.trip)
        except TripValidationError:
            self.fail("validate_pickup_before_delivery should pass for empty trip")

    def test_validate_pickup_before_delivery_only_pickup(self):
        """Test validate_pickup_before_delivery passes when order has only pickup in trip"""
        # Add only pickup stop (skip validation)
        pickup_trip_stop = TripStop(
            trip=self.trip,
            stop=self.pickup_stop,
            order=1,
            planned_arrival_time=time(10, 0)
        )
        pickup_trip_stop.save(skip_validation=True)

        # Should pass (no delivery to compare against)
        try:
            validate_pickup_before_delivery(self.trip)
        except TripValidationError:
            self.fail("validate_pickup_before_delivery should pass when only pickup exists")

    def test_validate_pickup_before_delivery_only_delivery(self):
        """Test validate_pickup_before_delivery passes when order has only delivery in trip"""
        # Add only delivery stop (skip validation)
        delivery_trip_stop = TripStop(
            trip=self.trip,
            stop=self.delivery_stop,
            order=1,
            planned_arrival_time=time(10, 0)
        )
        delivery_trip_stop.save(skip_validation=True)

        # Should pass (no pickup to compare against)
        try:
            validate_pickup_before_delivery(self.trip)
        except TripValidationError:
            self.fail("validate_pickup_before_delivery should pass when only delivery exists")

    def test_reorder_stops_endpoint_validates_pickup_before_delivery(self):
        """Test that reorder-stops endpoint validates pickup before delivery"""
        # Set up order with pickup and delivery stops
        pickup_ts = TripStop(
            trip=self.trip,
            stop=self.pickup_stop,
            order=1,
            planned_arrival_time=time(10, 0)
        )
        pickup_ts.save(skip_validation=True)

        delivery_ts = TripStop(
            trip=self.trip,
            stop=self.delivery_stop,
            order=2,
            planned_arrival_time=time(11, 0)
        )
        delivery_ts.save(skip_validation=True)

        from test_utils import AuthenticatedTestMixin
        from django.test import Client
        import json

        # Try to reorder so delivery comes before pickup (should fail)
        client = Client()
        # Get token from authenticated test mixin
        auth_mixin = AuthenticatedTestMixin()
        auth_mixin.setUp_auth()

        response = client.post(
            f'/api/trips/{self.trip.id}/reorder-stops/',
            data=json.dumps({
                "orders": [
                    {"id": delivery_ts.id, "order": 1},  # Delivery first
                    {"id": pickup_ts.id, "order": 2}    # Pickup second
                ]
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {auth_mixin.token.key}'
        )

        # Should return 400 with validation error
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('delivery stop', data['error'].lower())
        self.assertIn('pickup', data['error'].lower())
