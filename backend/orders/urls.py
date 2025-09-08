from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    GenerateFakeOrdersView,
    StopListCreateView,
    StopDetailView,
    GenerateFakeStopsView
)

urlpatterns = [
    # Order endpoints
    path('orders/', OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/generate-fake/', GenerateFakeOrdersView.as_view(), name='generate_fake_orders'),

    # Stop endpoints
    path('stops/', StopListCreateView.as_view(), name='stop_list_create'),
    path('stops/<int:pk>/', StopDetailView.as_view(), name='stop_detail'),
    path('stops/generate-fake/', GenerateFakeStopsView.as_view(), name='generate_fake_stops'),
]
