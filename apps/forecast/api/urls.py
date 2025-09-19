from django.urls import path
from .views import FeedPredictionView

urlpatterns = [
    path('predict/feed/', FeedPredictionView.as_view(), name='predict-feed'),
]
