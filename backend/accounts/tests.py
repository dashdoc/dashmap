from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
import json
from companies.models import Company
from .models import AuthToken, UserProfile

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            address='123 Test St'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            phone='555-1234'
        )
        
    def test_login_success(self):
        response = self.client.post('/api/auth/login/', 
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('token', data)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['company_id'], self.company.id)
        self.assertEqual(data['company_name'], 'Test Company')
        
        # Verify token was created
        token = AuthToken.objects.get(key=data['token'])
        self.assertEqual(token.user, self.user)
        
    def test_login_invalid_credentials(self):
        response = self.client.post('/api/auth/login/',
            data=json.dumps({
                'username': 'testuser',
                'password': 'wrongpass'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('Invalid credentials', data['error'])
        
    def test_login_missing_fields(self):
        response = self.client.post('/api/auth/login/',
            data=json.dumps({
                'username': 'testuser'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('Username and password required', data['error'])
        
    def test_login_user_without_profile(self):
        # Create user without profile
        user_no_profile = User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        
        response = self.client.post('/api/auth/login/',
            data=json.dumps({
                'username': 'noprofile',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn('company_id', data)
        self.assertNotIn('company_name', data)
        
    def test_logout_success(self):
        # First login to get token
        login_response = self.client.post('/api/auth/login/',
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        token = login_response.json()['token']
        
        # Now logout
        response = self.client.post('/api/auth/logout/',
            headers={'Authorization': f'Token {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('Successfully logged out', data['message'])
        
        # Verify token was deleted
        self.assertFalse(AuthToken.objects.filter(key=token).exists())
        
    def test_logout_invalid_token(self):
        response = self.client.post('/api/auth/logout/',
            headers={'Authorization': 'Token invalidtoken123'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('Invalid token', data['error'])
        
    def test_logout_no_token(self):
        response = self.client.post('/api/auth/logout/')
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('Authentication required', data['error'])

class TokenAuthenticationMiddlewareTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = AuthToken.objects.create(user=self.user)
        
    def test_api_requires_authentication(self):
        # Try to access API without token
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, 401)
        
        data = response.json()
        self.assertIn('Authentication required', data['error'])
        
    def test_api_with_valid_token(self):
        # Access API with valid token
        response = self.client.get('/api/companies/',
            headers={'Authorization': f'Token {self.token.key}'}
        )
        self.assertEqual(response.status_code, 200)
        
    def test_api_with_invalid_token(self):
        # Access API with invalid token
        response = self.client.get('/api/companies/',
            headers={'Authorization': 'Token invalidtoken123'}
        )
        self.assertEqual(response.status_code, 401)
        
        data = response.json()
        self.assertIn('Invalid token', data['error'])
        
    def test_api_with_malformed_auth_header(self):
        # Test various malformed auth headers
        malformed_headers = [
            'Bearer token123',
            'Token',
            'token123',
            'Token ',
        ]
        
        for header in malformed_headers:
            response = self.client.get('/api/companies/',
                headers={'Authorization': header}
            )
            self.assertEqual(response.status_code, 401)
            
    def test_login_endpoint_bypasses_auth(self):
        # Login endpoint should not require authentication
        response = self.client.post('/api/auth/login/',
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
    def test_admin_bypasses_auth(self):
        # Admin should bypass token auth (uses session auth)
        response = self.client.get('/admin/')
        # Should redirect to login, not return 401
        self.assertEqual(response.status_code, 302)
        
    def test_user_set_in_request(self):
        # Verify that the middleware sets request.user correctly
        # We'll use a simple API endpoint to test this
        Company.objects.create(name='Test Company', address='123 St')
        
        response = self.client.get('/api/companies/',
            headers={'Authorization': f'Token {self.token.key}'}
        )
        
        self.assertEqual(response.status_code, 200)
        # The fact that we get a 200 response means the user was set correctly

class AuthTokenModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_token_creation(self):
        token = AuthToken.objects.create(user=self.user)
        
        self.assertIsNotNone(token.key)
        self.assertEqual(len(token.key), 40)  # 20 bytes hex = 40 chars
        self.assertEqual(token.user, self.user)
        
    def test_token_uniqueness(self):
        token1 = AuthToken.objects.create(user=self.user)
        token2 = AuthToken.objects.create(user=self.user)
        
        self.assertNotEqual(token1.key, token2.key)
        
    def test_token_string_representation(self):
        token = AuthToken.objects.create(user=self.user)
        expected_str = f"Token for {self.user.username}"
        self.assertEqual(str(token), expected_str)
