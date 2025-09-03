from django.urls import path
from .views import (
    StopListCreateView, StopDetailView, GenerateFakeView,
    TripListCreateView, TripDetailView, TripNotifyDriverView,
    TripStopListCreateView, TripStopDetailView, TripStopReorderView
)

urlpatterns = [
    path('stops/', StopListCreateView.as_view(), name='stop-list-create'),
    path('stops/<int:pk>/', StopDetailView.as_view(), name='stop-detail'),
    path('stops/generate-fake/', GenerateFakeView.as_view(), name='generate-fake-stops'),
    path('trips/', TripListCreateView.as_view(), name='trip-list-create'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:pk>/notify-driver/', TripNotifyDriverView.as_view(), name='trip-notify-driver'),
    path('trip-stops/', TripStopListCreateView.as_view(), name='trip-stop-list-create'),
    path('trip-stops/<int:pk>/', TripStopDetailView.as_view(), name='trip-stop-detail'),
    path('trips/<int:trip_pk>/reorder-stops/', TripStopReorderView.as_view(), name='trip-stop-reorder'),
]
