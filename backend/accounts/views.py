from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import json
from .models import AuthToken, UserProfile
from companies.models import Company

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({'error': 'Username and password required'}, status=400)
            
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                # Delete existing tokens for this user (optional - for single session)
                AuthToken.objects.filter(user=user).delete()
                
                # Create new token
                token = AuthToken.objects.create(user=user)
                
                response_data = {
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
                
                # Add company info if user has profile
                try:
                    profile = user.profile
                    response_data.update({
                        'company_id': profile.company.id,
                        'company_name': profile.company.name
                    })
                except:
                    pass
                
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Authentication failed'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = AuthToken.objects.get(key=token_key)
                token.delete()
                return JsonResponse({'message': 'Successfully logged out'})
            except AuthToken.DoesNotExist:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return JsonResponse({'error': 'No token provided'}, status=401)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            company_name = data.get('company_name')
            company_address = data.get('company_address')
            company_phone = data.get('company_phone', '')
            company_email = data.get('company_email', '')
            
            if not all([username, password, email, first_name, last_name, company_name, company_address]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            # Create company
            company = Company.objects.create(
                name=company_name,
                address=company_address,
                phone=company_phone,
                email=company_email
            )
            
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                company=company
            )
            
            return JsonResponse({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Registration failed'}, status=500)

def get_user_from_token(request):
    """Utility function to get user from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
        try:
            token = AuthToken.objects.get(key=token_key)
            return token.user
        except AuthToken.DoesNotExist:
            return None
    return None
