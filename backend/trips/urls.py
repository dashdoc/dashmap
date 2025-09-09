from django.urls import path
from .views import (
    TripListCreateView, TripDetailView, TripNotifyDriverView,
    TripStopListView, TripStopDetailView, TripStopReorderView, TripAddOrderView
)

urlpatterns = [
    path('trips/', TripListCreateView.as_view(), name='trip-list-create'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:pk>/notify-driver/', TripNotifyDriverView.as_view(), name='trip-notify-driver'),
    path('trips/<int:trip_pk>/add-order/', TripAddOrderView.as_view(), name='trip-add-order'),
    path('trip-stops/', TripStopListView.as_view(), name='trip-stop-list'),
    path('trip-stops/<int:pk>/', TripStopDetailView.as_view(), name='trip-stop-detail'),
    path('trips/<int:trip_pk>/reorder-stops/', TripStopReorderView.as_view(), name='trip-stop-reorder'),
]
