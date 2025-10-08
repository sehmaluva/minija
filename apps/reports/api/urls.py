from django.urls import path
from apps.reports.api import views

urlpatterns = [
    path('', views.ReportListCreateView.as_view(), name='report_list_create'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('generate/', views.generate_report_view, name='generate_report'),

    path('alerts/', views.AlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/', views.AlertDetailView.as_view(), name='alert_detail'),
    path('alerts/create/', views.create_alert_view, name='create_alert'),
    path('alerts/bulk-update/', views.bulk_alert_update_view, name='bulk_alert_update'),

    path('analytics/dashboard/', views.analytics_dashboard_view, name='analytics_dashboard'),
]
