from django.urls import path
from .views import PositionListCreateView, GenerateFakeView, LatestPositionsView

urlpatterns = [
    path('positions/', PositionListCreateView.as_view(), name='position-list-create'),
    path('positions/latest/', LatestPositionsView.as_view(), name='latest-positions'),
    path('positions/generate-fake/', GenerateFakeView.as_view(), name='generate-fake-positions'),
]
