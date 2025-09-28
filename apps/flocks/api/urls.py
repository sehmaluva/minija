from django.urls import path
from apps.flocks.api import views

urlpatterns = [
    # Batch URLd
    path('', views.BatchListCreateView.as_view(), name='batch_list_create'),
    path('<int:pk>/', views.BatchDetailView.as_view(), name='batch_detail'),
    path('statistics/', views.batch_statistics_view, name='batch_statistics'),
    path('<int:batch_id>/performance/', views.batch_performance_view, name='batch_performance'),
    path('bulk-update/', views.bulk_batch_update_view, name='bulk_batch_update'),
    
    # Breed URLs
    # path('breeds/', views.BreedListCreateView.as_view(), name='breed_list_create'),
    # path('breeds/<int:pk>/', views.BreedDetailView.as_view(), name='breed_detail'),
    
    # Flock URLs
    # path('', views.FlockListCreateView.as_view(), name='flock_list_create'),
    # path('<int:pk>/', views.FlockDetailView.as_view(), name='flock_detail'),
    # path('statistics/', views.flock_statistics_view, name='flock_statistics'),
    # path('<int:flock_id>/performance/', views.flock_performance_view, name='flock_performance'),
    # path('bulk-update/', views.bulk_flock_update_view, name='bulk_flock_update'),
    
    # # Movement URLs
    # path('movements/', views.FlockMovementListCreateView.as_view(), name='movement_list_create'),
    # path('movements/<int:pk>/', views.FlockMovementDetailView.as_view(), name='movement_detail'),
]
