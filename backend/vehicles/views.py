from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Vehicle

@method_decorator(csrf_exempt, name='dispatch')
class VehicleListCreateView(View):
    def get(self, request):
        vehicles = Vehicle.objects.all()
        
        company_id = request.GET.get('company')
        if company_id:
            vehicles = vehicles.filter(company_id=company_id)
        
        data = []
        for vehicle in vehicles:
            data.append({
                'id': vehicle.id,
                'company': vehicle.company.id,
                'company_name': vehicle.company.name,
                'license_plate': vehicle.license_plate,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'capacity': str(vehicle.capacity),
                'driver_name': vehicle.driver_name,
                'driver_email': vehicle.driver_email,
                'driver_phone': vehicle.driver_phone,
                'is_active': vehicle.is_active,
                'created_at': vehicle.created_at.isoformat(),
                'updated_at': vehicle.updated_at.isoformat()
            })
        return JsonResponse({'results': data})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            vehicle = Vehicle.objects.create(
                company_id=data['company'],
                license_plate=data['license_plate'],
                make=data['make'],
                model=data['model'],
                year=data['year'],
                capacity=data['capacity'],
                driver_name=data['driver_name'],
                driver_email=data['driver_email'],
                driver_phone=data.get('driver_phone', ''),
                is_active=data.get('is_active', True)
            )
            return JsonResponse({
                'id': vehicle.id,
                'company': vehicle.company.id,
                'company_name': vehicle.company.name,
                'license_plate': vehicle.license_plate,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'capacity': str(vehicle.capacity),
                'driver_name': vehicle.driver_name,
                'driver_email': vehicle.driver_email,
                'driver_phone': vehicle.driver_phone,
                'is_active': vehicle.is_active,
                'created_at': vehicle.created_at.isoformat(),
                'updated_at': vehicle.updated_at.isoformat()
            }, status=201)
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class VehicleDetailView(View):
    def get_object(self, pk):
        try:
            return Vehicle.objects.select_related('company').get(pk=pk)
        except Vehicle.DoesNotExist:
            return None
    
    def get(self, request, pk):
        vehicle = self.get_object(pk)
        if not vehicle:
            return JsonResponse({'error': 'Vehicle not found'}, status=404)
        
        return JsonResponse({
            'id': vehicle.id,
            'company': vehicle.company.id,
            'company_name': vehicle.company.name,
            'license_plate': vehicle.license_plate,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'capacity': str(vehicle.capacity),
            'driver_name': vehicle.driver_name,
            'driver_email': vehicle.driver_email,
            'driver_phone': vehicle.driver_phone,
            'is_active': vehicle.is_active,
            'created_at': vehicle.created_at.isoformat(),
            'updated_at': vehicle.updated_at.isoformat()
        })
    
    def put(self, request, pk):
        vehicle = self.get_object(pk)
        if not vehicle:
            return JsonResponse({'error': 'Vehicle not found'}, status=404)
        
        try:
            data = json.loads(request.body)
            vehicle.company_id = data.get('company', vehicle.company_id)
            vehicle.license_plate = data.get('license_plate', vehicle.license_plate)
            vehicle.make = data.get('make', vehicle.make)
            vehicle.model = data.get('model', vehicle.model)
            vehicle.year = data.get('year', vehicle.year)
            vehicle.capacity = data.get('capacity', vehicle.capacity)
            vehicle.driver_name = data.get('driver_name', vehicle.driver_name)
            vehicle.driver_email = data.get('driver_email', vehicle.driver_email)
            vehicle.driver_phone = data.get('driver_phone', vehicle.driver_phone)
            vehicle.is_active = data.get('is_active', vehicle.is_active)
            vehicle.save()
            
            return JsonResponse({
                'id': vehicle.id,
                'company': vehicle.company.id,
                'company_name': vehicle.company.name,
                'license_plate': vehicle.license_plate,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'capacity': str(vehicle.capacity),
                'driver_name': vehicle.driver_name,
                'driver_email': vehicle.driver_email,
                'driver_phone': vehicle.driver_phone,
                'is_active': vehicle.is_active,
                'created_at': vehicle.created_at.isoformat(),
                'updated_at': vehicle.updated_at.isoformat()
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    def delete(self, request, pk):
        vehicle = self.get_object(pk)
        if not vehicle:
            return JsonResponse({'error': 'Vehicle not found'}, status=404)
        
        vehicle.delete()
        return JsonResponse({}, status=204)
