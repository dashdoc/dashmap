from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from companies.models import Company
from vehicles.models import Vehicle
from trips.models import Trip, TripStop
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

        # Create Dashmove company
        self.stdout.write('Creating Dashmove company...')
        dashmove = Company.objects.create(
            name='Dashmove',
            address='15 Avenue de la République, 75011 Paris, France',
            phone='+33-1-4555-DASH',
            email='contact@dashmove.eu'
        )

        # Link test user to Dashmove company
        self.stdout.write('Linking test user to Dashmove...')
        user_profile = UserProfile.objects.create(
            user=user,
            company=dashmove,
            phone='+33-6-TEST-USER'
        )


        # Create test vehicles
        self.stdout.write('Creating test vehicles...')
        vehicles_data = [
            # Dashmove heavy trucks fleet
            {'company': dashmove, 'plate': 'FR-001-DM', 'make': 'Volvo', 'model': 'FH16', 'year': 2023, 'capacity': 40.0, 'driver': 'Jean Dupont', 'email': 'jean@dashmove.eu', 'phone': '+33-6-01-02-03'},
            {'company': dashmove, 'plate': 'FR-002-DM', 'make': 'Scania', 'model': 'R730', 'year': 2022, 'capacity': 40.0, 'driver': 'Marie Dubois', 'email': 'marie@dashmove.eu', 'phone': '+33-6-04-05-06'},
            {'company': dashmove, 'plate': 'FR-003-DM', 'make': 'Mercedes-Benz', 'model': 'Actros', 'year': 2024, 'capacity': 40.0, 'driver': 'Pierre Martin', 'email': 'pierre@dashmove.eu', 'phone': '+33-6-07-08-09'},
            {'company': dashmove, 'plate': 'FR-004-DM', 'make': 'MAN', 'model': 'TGX', 'year': 2023, 'capacity': 40.0, 'driver': 'Sophie Bernard', 'email': 'sophie@dashmove.eu', 'phone': '+33-6-10-11-12'},
            {'company': dashmove, 'plate': 'FR-005-DM', 'make': 'DAF', 'model': 'XF', 'year': 2022, 'capacity': 40.0, 'driver': 'Laurent Moreau', 'email': 'laurent@dashmove.eu', 'phone': '+33-6-13-14-15'},
            {'company': dashmove, 'plate': 'FR-006-DM', 'make': 'Iveco', 'model': 'S-Way', 'year': 2024, 'capacity': 40.0, 'driver': 'Camille Rousseau', 'email': 'camille@dashmove.eu', 'phone': '+33-6-16-17-18'},
            {'company': dashmove, 'plate': 'FR-007-DM', 'make': 'Renault', 'model': 'T High', 'year': 2023, 'capacity': 40.0, 'driver': 'Thomas Leroy', 'email': 'thomas@dashmove.eu', 'phone': '+33-6-19-20-21'},
            {'company': dashmove, 'plate': 'FR-008-DM', 'make': 'Volvo', 'model': 'FH', 'year': 2022, 'capacity': 40.0, 'driver': 'Isabelle Garnier', 'email': 'isabelle@dashmove.eu', 'phone': '+33-6-22-23-24'},
            {'company': dashmove, 'plate': 'FR-009-DM', 'make': 'Scania', 'model': 'S650', 'year': 2024, 'capacity': 40.0, 'driver': 'Nicolas Blanc', 'email': 'nicolas@dashmove.eu', 'phone': '+33-6-25-26-27'},
            {'company': dashmove, 'plate': 'FR-010-DM', 'make': 'Mercedes-Benz', 'model': 'Arocs', 'year': 2023, 'capacity': 32.0, 'driver': 'Virginie Petit', 'email': 'virginie@dashmove.eu', 'phone': '+33-6-28-29-30'},
            {'company': dashmove, 'plate': 'FR-011-DM', 'make': 'MAN', 'model': 'TGS', 'year': 2022, 'capacity': 32.0, 'driver': 'Sébastien Roux', 'email': 'sebastien@dashmove.eu', 'phone': '+33-6-31-32-33'},
            {'company': dashmove, 'plate': 'FR-012-DM', 'make': 'DAF', 'model': 'CF', 'year': 2024, 'capacity': 26.0, 'driver': 'Caroline Faure', 'email': 'caroline@dashmove.eu', 'phone': '+33-6-34-35-36'},
            {'company': dashmove, 'plate': 'FR-013-DM', 'make': 'Iveco', 'model': 'Stralis', 'year': 2023, 'capacity': 26.0, 'driver': 'Julien Girard', 'email': 'julien@dashmove.eu', 'phone': '+33-6-37-38-39'},
            {'company': dashmove, 'plate': 'FR-014-DM', 'make': 'Renault', 'model': 'C', 'year': 2022, 'capacity': 26.0, 'driver': 'Nathalie Andre', 'email': 'nathalie@dashmove.eu', 'phone': '+33-6-40-41-42'},
            {'company': dashmove, 'plate': 'FR-015-DM', 'make': 'Volvo', 'model': 'FM', 'year': 2024, 'capacity': 26.0, 'driver': 'Olivier Mercier', 'email': 'olivier@dashmove.eu', 'phone': '+33-6-43-44-45'},
            {'company': dashmove, 'plate': 'FR-016-DM', 'make': 'Scania', 'model': 'G450', 'year': 2023, 'capacity': 26.0, 'driver': 'Sandrine Lefebvre', 'email': 'sandrine@dashmove.eu', 'phone': '+33-6-46-47-48'},
            {'company': dashmove, 'plate': 'FR-017-DM', 'make': 'Mercedes-Benz', 'model': 'Antos', 'year': 2022, 'capacity': 18.0, 'driver': 'Maxime Chevallier', 'email': 'maxime@dashmove.eu', 'phone': '+33-6-49-50-51'},
            {'company': dashmove, 'plate': 'FR-018-DM', 'make': 'MAN', 'model': 'TGL', 'year': 2024, 'capacity': 18.0, 'driver': 'Aurélie Fontaine', 'email': 'aurelie@dashmove.eu', 'phone': '+33-6-52-53-54'},
            {'company': dashmove, 'plate': 'FR-019-DM', 'make': 'DAF', 'model': 'LF', 'year': 2023, 'capacity': 18.0, 'driver': 'Christophe Morel', 'email': 'christophe@dashmove.eu', 'phone': '+33-6-55-56-57'},
            {'company': dashmove, 'plate': 'FR-020-DM', 'make': 'Iveco', 'model': 'Eurocargo', 'year': 2022, 'capacity': 18.0, 'driver': 'Céline Fournier', 'email': 'celine@dashmove.eu', 'phone': '+33-6-58-59-60'},
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
            # Major Distribution Centers & Warehouses (Loading)
            {'name': 'Rungis International Market', 'address': '1 Rue de la Tour, 94150 Rungis, France', 'lat': 48.759, 'lng': 2.352, 'type': 'loading', 'contact': 'Loading Supervisor', 'phone': '+33-1-41-80-8000'},
            {'name': 'Port of Le Havre Container Terminal', 'address': 'Terminal de France, 76600 Le Havre, France', 'lat': 49.490, 'lng': 0.120, 'type': 'loading', 'contact': 'Port Operations', 'phone': '+33-2-32-74-7400'},
            {'name': 'Lyon Eurexpo Logistics Hub', 'address': 'Chassieu Industrial Zone, 69680 Chassieu, France', 'lat': 45.736, 'lng': 4.966, 'type': 'loading', 'contact': 'Warehouse Manager', 'phone': '+33-4-72-22-3300'},
            {'name': 'Marseille Fos Port', 'address': 'Zone Industrielle de Fos, 13270 Fos-sur-Mer, France', 'lat': 43.407, 'lng': 4.947, 'type': 'loading', 'contact': 'Port Authority', 'phone': '+33-4-91-39-4000'},
            {'name': 'Toulouse Aerospace Freight', 'address': 'Aéroport Toulouse-Blagnac, 31700 Blagnac, France', 'lat': 43.635, 'lng': 1.363, 'type': 'loading', 'contact': 'Cargo Terminal', 'phone': '+33-5-34-50-5000'},
            {'name': 'Strasbourg Rhine Port', 'address': 'Port Autonome de Strasbourg, 67000 Strasbourg, France', 'lat': 48.564, 'lng': 7.788, 'type': 'loading', 'contact': 'Rhine Operations', 'phone': '+33-3-88-21-7300'},
            {'name': 'Lille Lesquin Industrial Zone', 'address': 'Zone Industrielle, 59810 Lesquin, France', 'lat': 50.584, 'lng': 3.118, 'type': 'loading', 'contact': 'Distribution Center', 'phone': '+33-3-20-62-5500'},
            {'name': 'Bordeaux Wine Export Hub', 'address': 'Port de Bordeaux, 33300 Bordeaux, France', 'lat': 44.857, 'lng': -0.545, 'type': 'loading', 'contact': 'Export Manager', 'phone': '+33-5-56-90-5800'},
            {'name': 'Nantes Atlantic Logistics', 'address': 'Zone Atlantis, 44800 Saint-Herblain, France', 'lat': 47.230, 'lng': -1.630, 'type': 'loading', 'contact': 'Logistics Coordinator', 'phone': '+33-2-40-94-5000'},
            {'name': 'Nancy Industrial Complex', 'address': 'Zone de Brabois, 54500 Vandœuvre-lès-Nancy, France', 'lat': 48.650, 'lng': 6.155, 'type': 'loading', 'contact': 'Plant Manager', 'phone': '+33-3-83-68-5200'},

            # Major Retail & Distribution Centers (Unloading)
            {'name': 'Carrefour Distribution Paris', 'address': '93 Avenue de Paris, 94300 Vincennes, France', 'lat': 48.847, 'lng': 2.428, 'type': 'unloading', 'contact': 'Receiving Manager', 'phone': '+33-1-55-93-7000'},
            {'name': 'Auchan Logistics Lyon', 'address': 'ZAC des Basses Barolles, 69124 Colombier-Saugnieu, France', 'lat': 45.726, 'lng': 5.098, 'type': 'unloading', 'contact': 'Warehouse Supervisor', 'phone': '+33-4-78-49-8500'},
            {'name': 'Leclerc Regional Center', 'address': 'Route de Sablé, 53200 Château-Gontier, France', 'lat': 47.828, 'lng': -0.705, 'type': 'unloading', 'contact': 'Store Operations', 'phone': '+33-2-43-09-4400'},
            {'name': 'Intermarché Distribution', 'address': 'Rue des Lilas, 49124 Saint-Barthélemy-d\'Anjou, France', 'lat': 47.460, 'lng': -0.515, 'type': 'unloading', 'contact': 'Receiving Clerk', 'phone': '+33-2-41-96-8000'},
            {'name': 'Casino Supply Chain', 'address': 'Rue Emile Romanet, 42000 Saint-Étienne, France', 'lat': 45.460, 'lng': 4.390, 'type': 'unloading', 'contact': 'Supply Manager', 'phone': '+33-4-77-45-3100'},
            {'name': 'Système U Platform', 'address': 'ZI de Kervillé, 56850 Caudan, France', 'lat': 47.805, 'lng': -3.344, 'type': 'unloading', 'contact': 'Platform Manager', 'phone': '+33-2-97-02-5500'},

            # International Destinations
            {'name': 'Brussels Cargo Hub', 'address': 'Rue du Progrès 80, 1210 Brussels, Belgium', 'lat': 50.854, 'lng': 4.357, 'type': 'unloading', 'contact': 'Belgian Operations', 'phone': '+32-2-204-1111'},
            {'name': 'Amsterdam Schiphol Cargo', 'address': 'Schiphol Boulevard 127, 1118 BG Schiphol, Netherlands', 'lat': 52.311, 'lng': 4.768, 'type': 'unloading', 'contact': 'Cargo Terminal', 'phone': '+31-20-601-9111'},
            {'name': 'Frankfurt Industrial Zone', 'address': 'Gutleutstraße 30, 60329 Frankfurt am Main, Germany', 'lat': 50.107, 'lng': 8.651, 'type': 'unloading', 'contact': 'German Distributor', 'phone': '+49-69-2640-0'},
            {'name': 'Milan Logistics Park', 'address': 'Via Milanofiori, 20090 Assago MI, Italy', 'lat': 45.389, 'lng': 9.128, 'type': 'unloading', 'contact': 'Italian Partner', 'phone': '+39-02-892-41'},
            {'name': 'Barcelona Port Container', 'address': 'Moll Adossat, 08039 Barcelona, Spain', 'lat': 41.354, 'lng': 2.177, 'type': 'unloading', 'contact': 'Spanish Operations', 'phone': '+34-93-306-8800'},
            {'name': 'Zurich Distribution Center', 'address': 'Industriestrasse 15, 8305 Dietlikon, Switzerland', 'lat': 47.416, 'lng': 8.614, 'type': 'unloading', 'contact': 'Swiss Logistics', 'phone': '+41-44-835-8100'},

            # Manufacturing & Industrial Sites
            {'name': 'Renault Flins Factory', 'address': 'Île de France, 78410 Flins-sur-Seine, France', 'lat': 48.964, 'lng': 1.875, 'type': 'unloading', 'contact': 'Factory Reception', 'phone': '+33-1-30-18-7000'},
            {'name': 'Airbus Toulouse Delivery', 'address': '316 Route de Bayonne, 31060 Toulouse, France', 'lat': 43.574, 'lng': 1.348, 'type': 'unloading', 'contact': 'Delivery Center', 'phone': '+33-5-61-93-3300'},
            {'name': 'Michelin Clermont-Ferrand', 'address': '12 Cours Sablon, 63000 Clermont-Ferrand, France', 'lat': 45.779, 'lng': 3.082, 'type': 'unloading', 'contact': 'Plant Logistics', 'phone': '+33-4-73-32-2000'},
            {'name': 'Total Refinery Normandy', 'address': '76700 Gonfreville-l\'Orcher, France', 'lat': 49.497, 'lng': 0.229, 'type': 'loading', 'contact': 'Refinery Operations', 'phone': '+33-2-35-22-3000'},
            {'name': 'Danone Evian Factory', 'address': 'Avenue des Mateirons, 74500 Évian-les-Bains, France', 'lat': 46.400, 'lng': 6.589, 'type': 'loading', 'contact': 'Production Planning', 'phone': '+33-4-50-84-8000'},

            # Regional Centers
            {'name': 'Reims Champagne Logistics', 'address': 'Avenue de Champagne, 51160 AY, France', 'lat': 49.058, 'lng': 4.006, 'type': 'loading', 'contact': 'Champagne Export', 'phone': '+33-3-26-54-4700'},
            {'name': 'Tours Loire Valley Hub', 'address': 'ZAC des Atlantes, 37270 Montlouis-sur-Loire, France', 'lat': 47.388, 'lng': 0.835, 'type': 'unloading', 'contact': 'Regional Manager', 'phone': '+33-2-47-45-5500'},
            {'name': 'Grenoble Alpine Center', 'address': 'ZAC de Comboire, 38130 Échirolles, France', 'lat': 45.145, 'lng': 5.714, 'type': 'unloading', 'contact': 'Alpine Logistics', 'phone': '+33-4-76-33-6600'},
            {'name': 'Brest Maritime Terminal', 'address': 'Port de Commerce, 29200 Brest, France', 'lat': 48.383, 'lng': -4.495, 'type': 'loading', 'contact': 'Maritime Operations', 'phone': '+33-2-98-43-4000'},
            {'name': 'Dijon Food Processing', 'address': 'ZI de Longvic, 21600 Longvic, France', 'lat': 47.286, 'lng': 5.042, 'type': 'loading', 'contact': 'Food Hub Manager', 'phone': '+33-3-80-68-7700'},
            {'name': 'Montpellier Tech Park', 'address': 'Parc Euromédecine, 34090 Montpellier, France', 'lat': 43.641, 'lng': 3.834, 'type': 'unloading', 'contact': 'Tech Delivery', 'phone': '+33-4-67-15-1500'},
            {'name': 'Rennes Bretagne Hub', 'address': 'ZAC Atalante Champeaux, 35000 Rennes, France', 'lat': 48.101, 'lng': -1.675, 'type': 'unloading', 'contact': 'Bretagne Logistics', 'phone': '+33-2-23-23-5000'},
            {'name': 'Metz Lorraine Center', 'address': 'Technopôle de Metz, 57070 Metz, France', 'lat': 49.109, 'lng': 6.229, 'type': 'unloading', 'contact': 'Lorraine Operations', 'phone': '+33-3-87-76-0600'},
            {'name': 'Perpignan Mediterranean', 'address': 'Avenue de Grande-Bretagne, 66000 Perpignan, France', 'lat': 42.688, 'lng': 2.895, 'type': 'loading', 'contact': 'Med Logistics', 'phone': '+33-4-68-85-0500'},
            {'name': 'Amiens Picardy Distribution', 'address': 'ZAC Jules Verne, 80440 Glisy, France', 'lat': 49.871, 'lng': 2.379, 'type': 'unloading', 'contact': 'Picardy Hub', 'phone': '+33-3-22-93-7000'},

            # Cross-Border Operations
            {'name': 'Calais Ferry Terminal', 'address': 'Avenue du Président Wilson, 62100 Calais, France', 'lat': 50.971, 'lng': 1.863, 'type': 'loading', 'contact': 'Ferry Operations', 'phone': '+33-3-21-46-4000'},
            {'name': 'Strasbourg Euro Hub', 'address': 'Rue du Port du Rhin, 67000 Strasbourg, France', 'lat': 48.586, 'lng': 7.789, 'type': 'unloading', 'contact': 'European Operations', 'phone': '+33-3-88-21-7800'},
            {'name': 'Geneva International', 'address': 'Route de l\'Aéroport 21, 1215 Geneva, Switzerland', 'lat': 46.238, 'lng': 6.109, 'type': 'unloading', 'contact': 'Swiss Customs', 'phone': '+41-22-717-7111'},
            {'name': 'Luxembourg Financial District', 'address': 'Boulevard Royal 2, 2449 Luxembourg', 'lat': 49.610, 'lng': 6.129, 'type': 'unloading', 'contact': 'Luxembourg Office', 'phone': '+352-4761-6200'},

            # Specialized Cargo Centers
            {'name': 'Orly Cargo Complex', 'address': 'Aéroport d\'Orly, 94390 Orly, France', 'lat': 48.723, 'lng': 2.359, 'type': 'loading', 'contact': 'Air Cargo', 'phone': '+33-1-49-75-1500'},
            {'name': 'Rouen Seine Port', 'address': '34 Boulevard Émile Duchemin, 76000 Rouen, France', 'lat': 49.428, 'lng': 1.064, 'type': 'loading', 'contact': 'River Transport', 'phone': '+33-2-35-52-5400'},
            {'name': 'Mulhouse Chemical Complex', 'address': 'Rue de l\'Industrie, 68200 Mulhouse, France', 'lat': 47.751, 'lng': 7.335, 'type': 'loading', 'contact': 'Chemical Logistics', 'phone': '+33-3-89-32-7200'},
            {'name': 'Dunkerque Steel Works', 'address': 'Route de Bourbourg, 59140 Dunkerque, France', 'lat': 51.034, 'lng': 2.376, 'type': 'loading', 'contact': 'Steel Operations', 'phone': '+33-3-28-29-3000'},
            {'name': 'Limoges Porcelain Export', 'address': 'Avenue de Louyat, 87280 Limoges, France', 'lat': 45.868, 'lng': 1.315, 'type': 'loading', 'contact': 'Export Specialist', 'phone': '+33-5-55-45-6700'},
            {'name': 'Troyes Textile Hub', 'address': 'Rue Marie Curie, 10600 La Chapelle-Saint-Luc, France', 'lat': 48.319, 'lng': 4.042, 'type': 'loading', 'contact': 'Textile Center', 'phone': '+33-3-25-71-2200'},

            # Construction & Building Materials
            {'name': 'Saint-Gobain Depot Melun', 'address': 'Avenue Thiers, 77000 Melun, France', 'lat': 48.537, 'lng': 2.661, 'type': 'loading', 'contact': 'Construction Supply', 'phone': '+33-1-64-79-3000'},
            {'name': 'Lafarge Cement Plant', 'address': 'Route de Cavaillon, 84300 Cavaillon, France', 'lat': 43.837, 'lng': 5.038, 'type': 'loading', 'contact': 'Cement Operations', 'phone': '+33-4-90-78-0100'},
            {'name': 'Bouygues Construction Supply', 'address': 'Avenue Eugène Freyssinet, 78280 Guyancourt, France', 'lat': 48.773, 'lng': 2.075, 'type': 'unloading', 'contact': 'Construction Logistics', 'phone': '+33-1-30-60-3300'},
            {'name': 'Vinci Materials Depot', 'address': 'Chemin des Sables, 95500 Gonesse, France', 'lat': 49.001, 'lng': 2.458, 'type': 'loading', 'contact': 'Materials Manager', 'phone': '+33-1-34-41-1100'},

            # Energy & Utilities
            {'name': 'EDF Nuclear Transport', 'address': 'Site de Gravelines, 59820 Gravelines, France', 'lat': 50.987, 'lng': 2.130, 'type': 'loading', 'contact': 'Nuclear Transport', 'phone': '+33-3-28-51-8000'},
            {'name': 'Engie Gas Distribution', 'address': 'Tour T1, 1 Place Samuel de Champlain, 92400 Courbevoie, France', 'lat': 48.896, 'lng': 2.237, 'type': 'unloading', 'contact': 'Gas Logistics', 'phone': '+33-1-44-22-0000'},
            {'name': 'TotalEnergies Depot', 'address': 'Raffinerie de Feyzin, 69320 Feyzin, France', 'lat': 45.673, 'lng': 4.857, 'type': 'loading', 'contact': 'Fuel Distribution', 'phone': '+33-4-72-21-7000'},

            # Pharmaceutical & Healthcare
            {'name': 'Sanofi Distribution Center', 'address': '54 Rue La Boétie, 75008 Paris, France', 'lat': 48.873, 'lng': 2.312, 'type': 'loading', 'contact': 'Pharma Logistics', 'phone': '+33-1-53-77-4000'},
            {'name': 'Servier Pharmaceutical Hub', 'address': '50 Rue Carnot, 92284 Suresnes, France', 'lat': 48.869, 'lng': 2.224, 'type': 'loading', 'contact': 'Medical Supply', 'phone': '+33-1-55-72-6000'},
            {'name': 'LVMH Luxury Logistics', 'address': '22 Avenue Montaigne, 75008 Paris, France', 'lat': 48.866, 'lng': 2.307, 'type': 'loading', 'contact': 'Luxury Goods', 'phone': '+33-1-44-13-2222'},

            # Agricultural & Food Processing
            {'name': 'Bonduelle Vegetable Processing', 'address': 'Avenue Louis Bonduelle, 59173 Renescure, France', 'lat': 50.725, 'lng': 2.361, 'type': 'loading', 'contact': 'Food Processing', 'phone': '+33-3-20-43-6060'},
            {'name': 'Lactalis Dairy Export', 'address': '10 Rue Adolphe Beck, 53000 Laval, France', 'lat': 48.073, 'lng': -0.766, 'type': 'loading', 'contact': 'Dairy Export', 'phone': '+33-2-43-59-2000'},
            {'name': 'Pernod Ricard Distribution', 'address': '12 Place des États-Unis, 75116 Paris, France', 'lat': 48.870, 'lng': 2.293, 'type': 'loading', 'contact': 'Beverage Export', 'phone': '+33-1-41-00-4200'},

            # Technology & Electronics
            {'name': 'Orange Telecom Equipment', 'address': 'Avenue Pierre Marzin, 22300 Lannion, France', 'lat': 48.732, 'lng': -3.459, 'type': 'loading', 'contact': 'Tech Equipment', 'phone': '+33-2-96-05-0000'},
            {'name': 'Schneider Electric Factory', 'address': '35 Rue Joseph Monier, 92500 Rueil-Malmaison, France', 'lat': 48.877, 'lng': 2.192, 'type': 'loading', 'contact': 'Electric Components', 'phone': '+33-1-41-29-7000'},
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

        # Create test orders
        self.stdout.write('Creating test orders...')
        loading_stops = [s for s in stops if s.stop_type == 'loading']
        unloading_stops = [s for s in stops if s.stop_type == 'unloading']

        # Create orders for the specific stops that will be used in trips
        # This ensures that trip stops will have associated orders
        trip_specific_orders = [
            # Order for Trip 1 (Paris to Marseille Export Route)
            # stops[0], stops[3], stops[9] -> Rungis, Marseille Port, Retail
            {
                'customer_name': 'ACME Manufacturing',
                'customer_company': 'ACME Corp',
                'customer_email': 'logistics@acme.com',
                'customer_phone': '+33-1-42-00-1234',
                'pickup_stop': stops[0],  # Rungis (loading)
                'delivery_stop': stops[9],  # A retail location (should be unloading)
                'goods_description': 'Fresh produce and dairy products',
                'goods_weight': 2500.0,
                'goods_volume': 15.0,
                'goods_type': 'refrigerated',
                'special_instructions': 'Keep temperature at 2-4°C throughout transport'
            },
            # Order for Trip 2 (Lyon Industrial Supply)
            # stops[2], stops[10], stops[12] -> Lyon Hub, Auchan, Casino
            {
                'customer_name': 'TechCorp Europe',
                'customer_company': 'TechCorp Ltd',
                'customer_email': 'supply@techcorp.eu',
                'customer_phone': '+33-1-45-67-8900',
                'pickup_stop': stops[2],  # Lyon Hub (loading)
                'delivery_stop': stops[10],  # Auchan (unloading)
                'goods_description': 'Industrial electronic components',
                'goods_weight': 850.0,
                'goods_volume': 5.2,
                'goods_type': 'fragile',
                'special_instructions': 'Handle with extreme care - sensitive electronics'
            },
            # Order for Trip 3 (Le Havre to Brussels)
            # stops[1], stops[16] -> Le Havre, Brussels
            {
                'customer_name': 'EuroConstruction',
                'customer_company': 'EuroConstruction SA',
                'customer_email': 'orders@euroconstruct.fr',
                'customer_phone': '+33-4-78-90-1234',
                'pickup_stop': stops[1],  # Le Havre (loading)
                'delivery_stop': stops[16],  # Brussels (unloading)
                'goods_description': 'Construction materials and tools',
                'goods_weight': 4200.0,
                'goods_volume': 28.0,
                'goods_type': 'standard',
                'special_instructions': 'Delivery to construction site - crane available'
            },
            # Order for Trip 4 (Toulouse Aerospace Delivery)
            # stops[4], stops[19], stops[21] -> Toulouse, Airbus, Tech
            {
                'customer_name': 'AeroSupply International',
                'customer_company': 'AeroSupply Ltd',
                'customer_email': 'urgent@aerosupply.com',
                'customer_phone': '+33-5-61-00-1234',
                'pickup_stop': stops[4],  # Toulouse Aerospace (loading)
                'delivery_stop': stops[19],  # Airbus (unloading)
                'goods_description': 'Aerospace manufacturing components',
                'goods_weight': 1200.0,
                'goods_volume': 8.5,
                'goods_type': 'standard',
                'special_instructions': 'Time-critical delivery for production line'
            },
            # Order for Trip 5 (Rhine Valley Route)
            # stops[5], stops[18], stops[22] -> Strasbourg, Frankfurt, Luxembourg
            {
                'customer_name': 'Rhine Logistics',
                'customer_company': 'Rhine Transport GmbH',
                'customer_email': 'operations@rhinetransport.de',
                'customer_phone': '+33-3-88-00-5678',
                'pickup_stop': stops[5],  # Strasbourg Rhine Port (loading)
                'delivery_stop': stops[18],  # Frankfurt (unloading)
                'goods_description': 'Industrial machinery parts',
                'goods_weight': 3200.0,
                'goods_volume': 18.0,
                'goods_type': 'oversized',
                'special_instructions': 'Requires special handling equipment'
            },
            # Additional orders for variety
            {
                'customer_name': 'PharmaLogistics',
                'customer_company': 'PharmaDistrib',
                'customer_email': 'urgent@pharmadistrib.com',
                'customer_phone': '+33-1-56-78-9012',
                'pickup_stop': loading_stops[9] if len(loading_stops) > 9 else loading_stops[0],  # Fallback to first if not enough
                'delivery_stop': unloading_stops[8] if len(unloading_stops) > 8 else unloading_stops[0],
                'goods_description': 'Pharmaceutical supplies and medications',
                'goods_weight': 320.0,
                'goods_volume': 2.8,
                'goods_type': 'hazmat',
                'special_instructions': 'Requires temperature monitoring and hazmat certification'
            },
            {
                'customer_name': 'Luxury Retail Chain',
                'customer_company': 'EliteStores International',
                'customer_email': 'procurement@elitestores.com',
                'customer_phone': '+33-1-44-55-6677',
                'pickup_stop': loading_stops[10] if len(loading_stops) > 10 else loading_stops[1],
                'delivery_stop': unloading_stops[10] if len(unloading_stops) > 10 else unloading_stops[1],
                'goods_description': 'Luxury fashion and accessories',
                'goods_weight': 180.0,
                'goods_volume': 8.5,
                'goods_type': 'fragile',
                'special_instructions': 'High-value goods - requires secure transport and signature on delivery'
            }
        ]

        orders = []
        for o_data in trip_specific_orders:
            order = Order.objects.create(
                customer_name=o_data['customer_name'],
                customer_company=o_data['customer_company'],
                customer_email=o_data['customer_email'],
                customer_phone=o_data['customer_phone'],
                pickup_stop=o_data['pickup_stop'],
                delivery_stop=o_data['delivery_stop'],
                goods_description=o_data['goods_description'],
                goods_weight=o_data['goods_weight'],
                goods_volume=o_data['goods_volume'],
                goods_type=o_data['goods_type'],
                special_instructions=o_data['special_instructions'],
                status='pending'
            )
            orders.append(order)

        self.stdout.write(f'Created {len(orders)} test orders')

        # Create test trips
        self.stdout.write('Creating test trips...')
        today = timezone.now().date()

        # Create 10 sample trips
        trips_data = [
            {
                'vehicle': vehicles[0],  # FR-001-DM
                'name': 'Paris to Marseille Export Route',
                'date': today,
                'start_time': '06:00:00',
                'status': 'in_progress',
                'stops': [stops[0], stops[3], stops[9]]  # Rungis -> Marseille Port -> Retail
            },
            {
                'vehicle': vehicles[1],  # FR-002-DM
                'name': 'Lyon Industrial Supply',
                'date': today,
                'start_time': '07:30:00',
                'status': 'planned',
                'stops': [stops[2], stops[10], stops[12]]  # Lyon Hub -> Auchan -> Casino
            },
            {
                'vehicle': vehicles[2],  # FR-003-DM
                'name': 'Le Havre to Brussels',
                'date': today,
                'start_time': '05:00:00',
                'status': 'completed',
                'stops': [stops[1], stops[16]]  # Le Havre -> Brussels
            },
            {
                'vehicle': vehicles[3],  # FR-004-DM
                'name': 'Toulouse Aerospace Delivery',
                'date': today,
                'start_time': '08:00:00',
                'status': 'planned',
                'stops': [stops[4], stops[19], stops[21]]  # Toulouse -> Airbus -> Tech
            },
            {
                'vehicle': vehicles[4],  # FR-005-DM
                'name': 'Rhine Valley Route',
                'date': today,
                'start_time': '06:30:00',
                'status': 'in_progress',
                'stops': [stops[5], stops[18], stops[22]]  # Strasbourg -> Frankfurt -> Luxembourg
            },
            {
                'vehicle': vehicles[5],  # FR-006-DM
                'name': 'Bordeaux Wine Export',
                'date': today + timedelta(days=1),
                'start_time': '09:00:00',
                'status': 'draft',
                'stops': [stops[7], stops[20]]  # Bordeaux -> Barcelona
            },
            {
                'vehicle': vehicles[6],  # FR-007-DM
                'name': 'Atlantic Coast Distribution',
                'date': today + timedelta(days=1),
                'start_time': '07:00:00',
                'status': 'draft',
                'stops': [stops[8], stops[11], stops[13]]  # Nantes -> Leclerc -> Intermarché
            },
            {
                'vehicle': vehicles[7],  # FR-008-DM
                'name': 'Champagne Region Export',
                'date': today,
                'start_time': '10:00:00',
                'status': 'planned',
                'stops': [stops[25], stops[17]]  # Reims -> Amsterdam
            },
            {
                'vehicle': vehicles[8],  # FR-009-DM
                'name': 'Manufacturing Supply Chain',
                'date': today,
                'start_time': '06:00:00',
                'status': 'in_progress',
                'stops': [stops[23], stops[24], stops[15]]  # Renault -> Michelin -> Milan
            },
            {
                'vehicle': vehicles[9],  # FR-010-DM
                'name': 'Cross-Border Logistics',
                'date': today + timedelta(days=2),
                'start_time': '05:30:00',
                'status': 'draft',
                'stops': [stops[30], stops[18], stops[21]]  # Calais -> Frankfurt -> Zurich
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
        # European major truck routes and cities
        base_locations = [
            (48.8566, 2.3522),   # Paris, France
            (45.7640, 4.8357),   # Lyon, France
            (43.2965, 5.3698),   # Marseille, France
            (50.8503, 4.3517),   # Brussels, Belgium
            (52.3676, 4.9041),   # Amsterdam, Netherlands
            (50.1109, 8.6821),   # Frankfurt, Germany
            (45.4642, 9.1900),   # Milan, Italy
            (41.3851, 2.1734),   # Barcelona, Spain
            (46.2044, 6.1432),   # Geneva, Switzerland
            (49.6116, 6.1319),   # Luxembourg
        ]

        total_positions = 0
        # Generate positions for more vehicles (10 out of 20)
        for i, vehicle in enumerate(vehicles[:10]):
            base_lat, base_lng = base_locations[i % len(base_locations)]

            # Create positions for the last 48 hours (more data for heavy trucks)
            current_time = timezone.now()
            for hour in range(48):
                timestamp = current_time - timedelta(hours=hour)

                # Add realistic heavy truck movement (smaller area, highways)
                lat_offset = random.uniform(-0.01, 0.01)  # Smaller range for highway routes
                lng_offset = random.uniform(-0.01, 0.01)

                Position.objects.create(
                    vehicle=vehicle,
                    latitude=base_lat + lat_offset,
                    longitude=base_lng + lng_offset,
                    speed=random.uniform(0, 90),  # Heavy truck highway speeds
                    heading=random.uniform(0, 360),
                    altitude=random.uniform(0, 800) if random.random() > 0.4 else None,  # European elevation
                    timestamp=timestamp,
                    odometer=random.uniform(50000, 150000),  # Heavy truck mileage
                    fuel_level=random.uniform(15, 95),
                    engine_status=random.choice(['on', 'idle', 'off'])  # More idle time for heavy trucks
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
        self.stdout.write(f'Trips: {Trip.objects.count()}')
        self.stdout.write(f'Positions: {Position.objects.count()}')
        self.stdout.write('\nTest data includes:')
        self.stdout.write('• Dashmove company with 20 heavy trucks (18-40 tons capacity)')
        self.stdout.write('• 7 sample orders with customer details, pickup/delivery locations, and goods information')
        self.stdout.write('• Orders specifically created to match trip stops for testing order linking')
        self.stdout.write('• 10 sample trips with different statuses')
        self.stdout.write('• 48 hours of position data for 10 vehicles across European routes')
        self.stdout.write('• Realistic heavy truck logistics operations')
        self.stdout.write('• European coordinates and addresses')
