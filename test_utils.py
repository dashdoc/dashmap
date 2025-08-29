from django.contrib.auth.models import User
from accounts.models import AuthToken

class AuthenticatedTestMixin:
    """Mixin to provide authentication helpers for API tests"""
    
    def setUp_auth(self):
        """Call this in your test setUp method"""
        self.auth_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        self.token = AuthToken.objects.create(user=self.auth_user)
        self.auth_headers = {'Authorization': f'Token {self.token.key}'}
    
    def authenticated_request(self, method, url, **kwargs):
        """Make an authenticated request"""
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update(self.auth_headers)
        return getattr(self.client, method.lower())(url, **kwargs)