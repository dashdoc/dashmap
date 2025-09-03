from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from companies.models import Company
from vehicles.models import Vehicle
from trips.models import Stop, Trip, TripStop
from positions.models import Position
from accounts.models import AuthToken, UserProfile

class Command(BaseCommand):
    help = 'Reset database with test data for local development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will DELETE ALL DATA in the database!\n'
                    'Run with --confirm flag to proceed.'
                )
            )
            return

        self.stdout.write(self.style.SUCCESS('Resetting database...'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Position.objects.all().delete()
        TripStop.objects.all().delete()
        Trip.objects.all().delete()
        Stop.objects.all().delete()
        Vehicle.objects.all().delete()
        UserProfile.objects.all().delete()
        Company.objects.all().delete()
        AuthToken.objects.all().delete()
        User.objects.all().delete()

        # Create test user
        self.stdout.write('Creating test user...')
        user = User.objects.create_user(
            username='test',
            password='test',
            email='test@dashmove.com',
            first_name='Test',
            last_name='User'
        )

        # Create auth token for the user
        token = AuthToken.objects.create(user=user)
        self.stdout.write(f'Created user "test" with password "test"')
        self.stdout.write(f'Auth token: {token.key}')

        # Create Dashmove company
        self.stdout.write('Creating Dashmove company...')
        dashmove = Company.objects.create(
            name='Dashmove',
            address='123 Tech Street, San Francisco, CA 94105',
            phone='555-DASH-MOVE',
            email='contact@dashmove.com'
        )

        # Link test user to Dashmove company
        self.stdout.write('Linking test user to Dashmove...')
        user_profile = UserProfile.objects.create(
            user=user,
            company=dashmove,
            phone='555-TEST-USER'
        )

        # Create additional test companies
        acme_logistics = Company.objects.create(
            name='ACME Logistics',
            address='456 Industrial Ave, Los Angeles, CA 90210',
            phone='555-ACME-LOG',
            email='info@acmelogistics.com'
        )

        swift_delivery = Company.objects.create(
            name='Swift Delivery',
            address='789 Commerce Blvd, Chicago, IL 60601',
            phone='555-SWIFT-GO',
            email='hello@swiftdelivery.com'
        )

        # Create test vehicles
        self.stdout.write('Creating test vehicles...')
        vehicles_data = [
            # Dashmove vehicles
            {'company': dashmove, 'plate': 'DASH-001', 'make': 'Ford', 'model': 'Transit', 'year': 2023, 'capacity': 2.5, 'driver': 'John Smith', 'email': 'john@dashmove.com', 'phone': '555-0001'},
            {'company': dashmove, 'plate': 'DASH-002', 'make': 'Mercedes', 'model': 'Sprinter', 'year': 2022, 'capacity': 3.0, 'driver': 'Maria Garcia', 'email': 'maria@dashmove.com', 'phone': '555-0002'},
            {'company': dashmove, 'plate': 'DASH-003', 'make': 'Iveco', 'model': 'Daily', 'year': 2024, 'capacity': 4.5, 'driver': 'Ahmed Hassan', 'email': 'ahmed@dashmove.com', 'phone': '555-0003'},

            # ACME Logistics vehicles
            {'company': acme_logistics, 'plate': 'ACME-100', 'make': 'Chevrolet', 'model': 'Express', 'year': 2021, 'capacity': 2.0, 'driver': 'Sarah Johnson', 'email': 'sarah@acmelogistics.com', 'phone': '555-0100'},
            {'company': acme_logistics, 'plate': 'ACME-101', 'make': 'Ford', 'model': 'E-Series', 'year': 2020, 'capacity': 3.5, 'driver': 'Mike Wilson', 'email': 'mike@acmelogistics.com', 'phone': '555-0101'},

            # Swift Delivery vehicles
            {'company': swift_delivery, 'plate': 'SWIFT-X1', 'make': 'Ram', 'model': 'ProMaster', 'year': 2023, 'capacity': 2.8, 'driver': 'Lisa Chen', 'email': 'lisa@swiftdelivery.com', 'phone': '555-0201'},
            {'company': swift_delivery, 'plate': 'SWIFT-X2', 'make': 'Nissan', 'model': 'NV200', 'year': 2022, 'capacity': 1.5, 'driver': 'Carlos Rodriguez', 'email': 'carlos@swiftdelivery.com', 'phone': '555-0202'},
        ]

        vehicles = []
        for v_data in vehicles_data:
            vehicle = Vehicle.objects.create(
                company=v_data['company'],
                license_plate=v_data['plate'],
                make=v_data['make'],
                model=v_data['model'],
                year=v_data['year'],
                capacity=v_data['capacity'],
                driver_name=v_data['driver'],
                driver_email=v_data['email'],
                driver_phone=v_data['phone'],
                is_active=True
            )
            vehicles.append(vehicle)

        self.stdout.write(f'Created {len(vehicles)} test vehicles')

        # Create test stops
        self.stdout.write('Creating test stops...')
        stops_data = [
            # Loading stops
            {'name': 'Main Warehouse', 'address': '100 Warehouse District, San Francisco, CA', 'lat': 37.7749, 'lng': -122.4194, 'type': 'loading', 'contact': 'Warehouse Manager', 'phone': '555-WAREHOUSE'},
            {'name': 'Distribution Center A', 'address': '200 Industrial Way, Oakland, CA', 'lat': 37.8044, 'lng': -122.2711, 'type': 'loading', 'contact': 'Loading Supervisor', 'phone': '555-DIST-A'},
            {'name': 'Supply Hub', 'address': '300 Commerce St, San Jose, CA', 'lat': 37.3382, 'lng': -121.8863, 'type': 'loading', 'contact': 'Hub Coordinator', 'phone': '555-SUPPLY'},

            # Unloading stops
            {'name': 'Downtown Store', 'address': '401 Market Street, San Francisco, CA', 'lat': 37.7879, 'lng': -122.3998, 'type': 'unloading', 'contact': 'Store Manager', 'phone': '555-STORE-1'},
            {'name': 'Mall Distribution Point', 'address': '500 Shopping Center Dr, Palo Alto, CA', 'lat': 37.4419, 'lng': -122.1430, 'type': 'unloading', 'contact': 'Receiving Clerk', 'phone': '555-MALL-1'},
            {'name': 'Restaurant Chain Hub', 'address': '600 Food Service Ave, Fremont, CA', 'lat': 37.5485, 'lng': -121.9886, 'type': 'unloading', 'contact': 'Kitchen Manager', 'phone': '555-FOOD-1'},
            {'name': 'Pharmacy Network', 'address': '700 Health Plaza, Mountain View, CA', 'lat': 37.3861, 'lng': -122.0839, 'type': 'unloading', 'contact': 'Pharmacy Lead', 'phone': '555-PHARMA'},
            {'name': 'Office Complex', 'address': '800 Business Park Dr, Sunnyvale, CA', 'lat': 37.3688, 'lng': -122.0363, 'type': 'unloading', 'contact': 'Office Manager', 'phone': '555-OFFICE'},
        ]

        stops = []
        for s_data in stops_data:
            stop = Stop.objects.create(
                name=s_data['name'],
                address=s_data['address'],
                latitude=s_data['lat'],
                longitude=s_data['lng'],
                stop_type=s_data['type'],
                contact_name=s_data['contact'],
                contact_phone=s_data['phone'],
                notes=f"Test {s_data['type']} location"
            )
            stops.append(stop)

        self.stdout.write(f'Created {len(stops)} test stops')

        # Create test trips
        self.stdout.write('Creating test trips...')
        today = timezone.now().date()

        # Create a few sample trips
        trips_data = [
            {
                'vehicle': vehicles[0],  # DASH-001
                'name': 'Morning Delivery Route',
                'date': today,
                'start_time': '08:00:00',
                'status': 'planned',
                'stops': [stops[0], stops[3], stops[4]]  # Warehouse -> Downtown -> Mall
            },
            {
                'vehicle': vehicles[1],  # DASH-002
                'name': 'Afternoon Supply Run',
                'date': today,
                'start_time': '10:00:00',
                'status': 'in_progress',
                'stops': [stops[1], stops[5], stops[6]]  # Distribution -> Restaurant -> Pharmacy
            },
            {
                'vehicle': vehicles[3],  # ACME-100
                'name': 'Next Day Office Delivery',
                'date': today + timedelta(days=1),
                'start_time': '09:30:00',
                'status': 'draft',
                'stops': [stops[2], stops[7]]  # Supply -> Office
            }
        ]

        trips = []
        for i, t_data in enumerate(trips_data):
            trip = Trip.objects.create(
                vehicle=t_data['vehicle'],
                dispatcher=user,  # Use our test user as dispatcher
                name=t_data['name'],
                planned_start_date=t_data['date'],
                planned_start_time=datetime.strptime(t_data['start_time'], '%H:%M:%S').time(),
                status=t_data['status'],
                notes=f'Test trip #{i+1} - Created by reset_db command'
            )

            # Add stops to trip
            base_time = datetime.strptime(t_data['start_time'], '%H:%M:%S').time()
            for j, stop in enumerate(t_data['stops']):
                # Calculate planned arrival time (adding hours for each subsequent stop)
                arrival_time = (datetime.combine(today, base_time) + timedelta(hours=j + 1)).time()

                TripStop.objects.create(
                    trip=trip,
                    stop=stop,
                    order=j + 1,
                    planned_arrival_time=arrival_time,
                    notes=f'Stop {j+1} of {len(t_data["stops"])}'
                )

            trips.append(trip)

        self.stdout.write(f'Created {len(trips)} test trips')

        # Create test positions for active vehicles
        self.stdout.write('Creating test position data...')
        base_locations = [
            (37.7749, -122.4194),  # San Francisco
            (37.8044, -122.2711),  # Oakland
            (37.3382, -121.8863),  # San Jose
        ]

        total_positions = 0
        for i, vehicle in enumerate(vehicles[:3]):  # Only for first 3 vehicles
            base_lat, base_lng = base_locations[i % len(base_locations)]

            # Create positions for the last 24 hours
            current_time = timezone.now()
            for hour in range(24):
                timestamp = current_time - timedelta(hours=hour)

                # Add some realistic movement
                lat_offset = random.uniform(-0.02, 0.02)
                lng_offset = random.uniform(-0.02, 0.02)

                Position.objects.create(
                    vehicle=vehicle,
                    latitude=base_lat + lat_offset,
                    longitude=base_lng + lng_offset,
                    speed=random.uniform(0, 65),
                    heading=random.uniform(0, 360),
                    altitude=random.uniform(0, 150) if random.random() > 0.3 else None,
                    timestamp=timestamp,
                    odometer=random.uniform(15000, 45000),
                    fuel_level=random.uniform(20, 95),
                    engine_status=random.choice(['on', 'off', 'idle'])
                )
                total_positions += 1

        self.stdout.write(f'Created {total_positions} position records')

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DATABASE RESET COMPLETE!'))
        self.stdout.write('='*50)
        self.stdout.write(f'Test User: username="test", password="test"')
        self.stdout.write(f'Auth Token: {token.key}')
        self.stdout.write(f'Companies: {Company.objects.count()}')
        self.stdout.write(f'Vehicles: {Vehicle.objects.count()}')
        self.stdout.write(f'Stops: {Stop.objects.count()}')
        self.stdout.write(f'Trips: {Trip.objects.count()}')
        self.stdout.write(f'Positions: {Position.objects.count()}')
        self.stdout.write('\nTest data includes:')
        self.stdout.write('• Dashmove company with 3 vehicles')
        self.stdout.write('• ACME Logistics with 2 vehicles')
        self.stdout.write('• Swift Delivery with 2 vehicles')
        self.stdout.write('• Sample trips with different statuses')
        self.stdout.write('• 24 hours of position data for 3 vehicles')
        self.stdout.write('• Various loading/unloading stops')
