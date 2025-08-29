from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.serializers import serialize
import json
from .models import Company

@method_decorator(csrf_exempt, name='dispatch')
class CompanyListCreateView(View):
    def get(self, request):
        companies = Company.objects.all()
        data = []
        for company in companies:
            data.append({
                'id': company.id,
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'email': company.email,
                'created_at': company.created_at.isoformat(),
                'updated_at': company.updated_at.isoformat()
            })
        return JsonResponse({'results': data})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            company = Company.objects.create(
                name=data['name'],
                address=data['address'],
                phone=data.get('phone', ''),
                email=data.get('email', '')
            )
            return JsonResponse({
                'id': company.id,
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'email': company.email,
                'created_at': company.created_at.isoformat(),
                'updated_at': company.updated_at.isoformat()
            }, status=201)
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'error': 'Invalid data'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class CompanyDetailView(View):
    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return None
    
    def get(self, request, pk):
        company = self.get_object(pk)
        if not company:
            return JsonResponse({'error': 'Company not found'}, status=404)
        
        return JsonResponse({
            'id': company.id,
            'name': company.name,
            'address': company.address,
            'phone': company.phone,
            'email': company.email,
            'created_at': company.created_at.isoformat(),
            'updated_at': company.updated_at.isoformat()
        })
    
    def put(self, request, pk):
        company = self.get_object(pk)
        if not company:
            return JsonResponse({'error': 'Company not found'}, status=404)
        
        try:
            data = json.loads(request.body)
            company.name = data.get('name', company.name)
            company.address = data.get('address', company.address)
            company.phone = data.get('phone', company.phone)
            company.email = data.get('email', company.email)
            company.save()
            
            return JsonResponse({
                'id': company.id,
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'email': company.email,
                'created_at': company.created_at.isoformat(),
                'updated_at': company.updated_at.isoformat()
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    def delete(self, request, pk):
        company = self.get_object(pk)
        if not company:
            return JsonResponse({'error': 'Company not found'}, status=404)
        
        company.delete()
        return JsonResponse({}, status=204)
