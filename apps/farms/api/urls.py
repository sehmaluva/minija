from django.urls import path
from apps.farms.api import views

urlpatterns = [
    path('', views.FarmListCreateView.as_view(), name='farm_list_create'),
    path('<int:pk>/', views.FarmDetailView.as_view(), name='farm_detail'),
    path('summary/', views.farm_summary_view, name='farm_summary'),
    path('<int:farm_id>/occupancy/', views.building_occupancy_view, name='building_occupancy'),
    
    path('buildings/', views.BuildingListCreateView.as_view(), name='building_list_create'),
    path('buildings/<int:pk>/', views.BuildingDetailView.as_view(), name='building_detail'),
]
