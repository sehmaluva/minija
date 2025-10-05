from django.urls import path
from apps.birds.api import views

urlpatterns = [
    # Batch URLd
    path('', views.BatchListCreateView.as_view(), name='batch_list_create'),
    path('<int:pk>/', views.BatchDetailView.as_view(), name='batch_detail'),
    path('statistics/', views.batch_statistics_view, name='batch_statistics'),
    path('<int:batch_id>/performance/', views.batch_performance_view, name='batch_performance'),
    path('bulk-update/', views.bulk_batch_update_view, name='bulk_batch_update'),

]
