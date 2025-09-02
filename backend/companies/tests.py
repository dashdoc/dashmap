from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
import json
from .models import Company
from test_utils import AuthenticatedTestMixin

class CompanyAPITestCase(TestCase, AuthenticatedTestMixin):
    def setUp(self):
        self.setUp_auth()  # Set up authentication
        self.company_data = {
            'name': 'Test Company',
            'address': '123 Test St',
            'phone': '555-0123',
            'email': 'test@company.com'
        }
        self.company = Company.objects.create(**self.company_data)

    def test_get_companies_list(self):
        response = self.authenticated_request('GET', '/api/companies/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

        company_data = data['results'][0]
        self.assertEqual(company_data['name'], 'Test Company')
        self.assertEqual(company_data['address'], '123 Test St')

    def test_create_company(self):
        new_company_data = {
            'name': 'New Company',
            'address': '456 New St',
            'phone': '555-0456',
            'email': 'new@company.com'
        }

        response = self.authenticated_request(
            'POST',
            '/api/companies/',
            data=json.dumps(new_company_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'New Company')

        # Verify company was created in database
        self.assertTrue(Company.objects.filter(name='New Company').exists())

    def test_get_company_detail(self):
        response = self.authenticated_request('GET', f'/api/companies/{self.company.id}/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], 'Test Company')
        self.assertEqual(data['id'], self.company.id)

    def test_update_company(self):
        updated_data = {
            'name': 'Updated Company',
            'address': '789 Updated St'
        }

        response = self.authenticated_request(
            'PUT',
            f'/api/companies/{self.company.id}/',
            data=json.dumps(updated_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Updated Company')

        # Verify update in database
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Updated Company')

    def test_delete_company(self):
        response = self.authenticated_request('DELETE', f'/api/companies/{self.company.id}/')
        self.assertEqual(response.status_code, 204)

        # Verify deletion
        self.assertFalse(Company.objects.filter(id=self.company.id).exists())

    def test_get_nonexistent_company(self):
        response = self.authenticated_request('GET', '/api/companies/999/')
        self.assertEqual(response.status_code, 404)

    def test_create_company_invalid_data(self):
        invalid_data = {'name': ''}  # Missing required fields

        response = self.authenticated_request(
            'POST',
            '/api/companies/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
