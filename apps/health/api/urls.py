from django.urls import path
from apps.health.api import views

urlpatterns = [
    path('records/', views.HealthRecordListCreateView.as_view(), name='health_record_list_create'),
    path('records/<int:pk>/', views.HealthRecordDetailView.as_view(), name='health_record_detail'),
    path('mortality/', views.MortalityRecordListCreateView.as_view(), name='mortality_record_list_create'),
    path('mortality/<int:pk>/', views.MortalityRecordDetailView.as_view(), name='mortality_record_detail'),
    path('dashboard/', views.health_dashboard_view, name='health_dashboard'),
    path('flock/<int:flock_id>/history/', views.flock_health_history_view, name='flock_health_history'),
]