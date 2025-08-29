from django.http import JsonResponse
from django.urls import reverse
from .models import AuthToken

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for login endpoints and admin
        skip_auth_paths = ['/api/auth/login/', '/admin/']
        
        if any(request.path.startswith(path) for path in skip_auth_paths):
            return self.get_response(request)
        
        # Only require auth for API endpoints
        if request.path.startswith('/api/'):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Token '):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            token_key = auth_header.split(' ')[1]
            try:
                token = AuthToken.objects.get(key=token_key)
                request.user = token.user
            except AuthToken.DoesNotExist:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return self.get_response(request)