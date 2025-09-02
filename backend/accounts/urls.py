from django.urls import path
from .views import LoginView, LogoutView, RegisterView, UserProfileUpdateView, CompanyUpdateView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/profile/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('auth/company/', CompanyUpdateView.as_view(), name='company-update'),
]
