from django.urls import path
from .views import PositionListCreateView, GenerateFakeView

urlpatterns = [
    path('positions/', PositionListCreateView.as_view(), name='position-list-create'),
    path('positions/generate-fake/', GenerateFakeView.as_view(), name='generate-fake-positions'),
]
