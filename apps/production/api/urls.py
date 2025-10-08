from django.urls import path
from apps.production.api import views

urlpatterns = [
    path(
        "feed/",
        views.FeedRecordListCreateView.as_view(),
        name="feed_record_list_create",
    ),
    path(
        "eggs/",
        views.EggProductionListCreateView.as_view(),
        name="egg_production_list_create",
    ),
    path(
        "weights/",
        views.WeightRecordListCreateView.as_view(),
        name="weight_record_list_create",
    ),
    path(
        "environmental/",
        views.EnvironmentalRecordListCreateView.as_view(),
        name="environmental_record_list_create",
    ),
    path("dashboard/", views.production_dashboard_view, name="production_dashboard"),
    path(
        "batch/<int:batch_id>/analysis/",
        views.batch_production_analysis_view,
        name="batch_production_analysis",
    ),
]
