from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    GenerateFakeOrdersView
)

urlpatterns = [
    # Order endpoints
    path('orders/', OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/generate-fake/', GenerateFakeOrdersView.as_view(), name='generate_fake_orders'),
]
