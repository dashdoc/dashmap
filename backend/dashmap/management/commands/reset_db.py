from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from faker import Faker
from companies.models import Company
from vehicles.models import Vehicle
from trips.models import Trip, TripStop
from trips.services import get_orders_requiring_both_stops, add_order_to_trip
from orders.models import Stop, Order
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

        fake = Faker(['fr_FR', 'en_US', 'de_DE', 'it_IT', 'es_ES'])
        Faker.seed(42)  # For reproducible test data

        self.stdout.write(self.style.SUCCESS('Resetting database...'))

        # Clear existing data (order matters due to foreign key constraints)
        self.stdout.write('Clearing existing data...')
        Position.objects.all().delete()
        TripStop.objects.all().delete()
        Trip.objects.all().delete()
        Order.objects.all().delete()  # Delete orders before stops
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

        # Create company
        self.stdout.write('Creating test company...')
        company = Company.objects.create(
            name='Dashmove',
            address=fake.address(),
            phone=fake.phone_number(),
            email='contact@dashmove.eu'
        )

        # Link test user to company
        user_profile = UserProfile.objects.create(
            user=user,
            company=company,
            phone=fake.phone_number()
        )

        # Create test vehicles
        self.stdout.write('Creating test vehicles...')
        truck_makes = ['Volvo', 'Scania', 'Mercedes-Benz', 'MAN', 'DAF', 'Iveco', 'Renault']
        truck_models = {
            'Volvo': ['FH16', 'FH', 'FM'],
            'Scania': ['R730', 'S650', 'G450'],
            'Mercedes-Benz': ['Actros', 'Arocs', 'Antos'],
            'MAN': ['TGX', 'TGS', 'TGL'],
            'DAF': ['XF', 'CF', 'LF'],
            'Iveco': ['S-Way', 'Stralis', 'Eurocargo'],
            'Renault': ['T High', 'C']
        }

        vehicles = []
        for i in range(20):
            make = fake.random_element(truck_makes)
            model = fake.random_element(truck_models[make])
            vehicle = Vehicle.objects.create(
                company=company,
                license_plate=f'FR-{i+1:03d}-DM',
                make=make,
                model=model,
                year=fake.random_int(min=2020, max=2024),
                capacity=fake.random_element([18.0, 26.0, 32.0, 40.0]),
                driver_name=fake.name(),
                driver_email=fake.email(),
                driver_phone=fake.phone_number(),
                is_active=True
            )
            vehicles.append(vehicle)

        self.stdout.write(f'Created {len(vehicles)} test vehicles')

        # Create test orders first, then create stops linked to orders
        self.stdout.write('Creating test orders and stops...')
        orders = []
        all_stops = []

        for i in range(15):
            # Create order
            order = Order.objects.create(
                customer_name=fake.company(),
                customer_company=fake.company(),
                customer_email=fake.email(),
                customer_phone=fake.phone_number(),
                goods_description=fake.text(max_nb_chars=100),
                goods_weight=fake.random_int(min=100, max=5000),
                goods_volume=fake.random_int(min=1, max=30),
                goods_type=fake.random_element(['standard', 'fragile', 'hazmat', 'refrigerated', 'oversized']),
                special_instructions=fake.sentence(),
                status='pending'
            )
            orders.append(order)

            # Create pickup stop for this order
            pickup_coords = fake.local_latlng(country_code='FR')
            pickup_stop = Stop.objects.create(
                order=order,
                name=f"{fake.company()} Warehouse",
                address=fake.address(),
                latitude=pickup_coords[0],
                longitude=pickup_coords[1],
                stop_type='pickup',
                contact_name=fake.name(),
                contact_phone=fake.phone_number(),
                notes='Pickup location'
            )
            all_stops.append(pickup_stop)

            # Create delivery stop for this order
            delivery_coords = fake.local_latlng(country_code='FR')
            delivery_stop = Stop.objects.create(
                order=order,
                name=f"{fake.company()} Distribution Center",
                address=fake.address(),
                latitude=delivery_coords[0],
                longitude=delivery_coords[1],
                stop_type='delivery',
                contact_name=fake.name(),
                contact_phone=fake.phone_number(),
                notes='Delivery location'
            )
            all_stops.append(delivery_stop)

        self.stdout.write(f'Created {len(orders)} test orders with {len(all_stops)} stops')


        # Create test trips with complete pickup/delivery pairs
        self.stdout.write('Creating test trips...')

        trips = []
        statuses = ['draft', 'planned', 'in_progress', 'completed']

        # Get orders that have both pickup and delivery stops
        complete_orders = get_orders_requiring_both_stops()

        for i in range(10):
            trip = Trip.objects.create(
                vehicle=fake.random_element(vehicles),
                dispatcher=user,
                name=f"{fake.city()} Delivery Route",
                planned_start_date=fake.date_between(start_date='today', end_date='+30d'),
                planned_start_time=fake.time(),
                status=fake.random_element(statuses),
                notes=fake.sentence()
            )

            # Add complete orders (pickup + delivery pairs) to trip
            num_orders = fake.random_int(min=1, max=2)  # 1-2 complete orders per trip
            selected_orders = fake.random_elements(elements=complete_orders, length=num_orders, unique=True)

            for order in selected_orders:
                # Generate times - pickup first, delivery after
                pickup_time = fake.time()
                delivery_time = fake.time()
                while delivery_time <= pickup_time:
                    delivery_time = fake.time()

                # Add the complete order to the trip
                add_order_to_trip(
                    trip=trip,
                    order=order,
                    pickup_time=pickup_time,
                    delivery_time=delivery_time
                )

            trips.append(trip)

        self.stdout.write(f'Created {len(trips)} test trips with complete pickup/delivery pairs')

        # Create test positions for active vehicles
        self.stdout.write('Creating test position data...')
        total_positions = 0

        # Generate positions for half the vehicles
        for vehicle in vehicles[:10]:
            # Create positions for the last 24 hours
            for _ in range(24):
                coords = fake.local_latlng(country_code='FR')
                Position.objects.create(
                    vehicle=vehicle,
                    latitude=coords[0],
                    longitude=coords[1],
                    speed=fake.random_int(min=0, max=90),
                    heading=fake.random_int(min=0, max=360),
                    altitude=fake.random_int(min=0, max=800) if fake.boolean() else None,
                    timestamp=fake.date_time_between(start_date='-1d', end_date='now', tzinfo=timezone.get_current_timezone()),
                    odometer=fake.random_int(min=50000, max=150000),
                    fuel_level=fake.random_int(min=15, max=95),
                    engine_status=fake.random_element(['on', 'idle', 'off'])
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
        self.stdout.write(f'Orders: {Order.objects.count()}')
        self.stdout.write(f'Stops: {Stop.objects.count()}')
        self.stdout.write(f'Trips: {Trip.objects.count()}')
        self.stdout.write(f'Positions: {Position.objects.count()}')
        self.stdout.write('\nTest data includes:')
        self.stdout.write('• Dashmove company with 20 realistic vehicles')
        self.stdout.write('• 15 orders with pickup and delivery stops (every stop belongs to an order)')
        self.stdout.write('• 10 trips with complete pickup/delivery pairs (ensuring order integrity)')
        self.stdout.write('• 24 hours of position data for 10 vehicles')
        self.stdout.write('• All data generated using Faker with French localization')
