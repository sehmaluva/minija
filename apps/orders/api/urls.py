from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChickOrderViewSet, ReminderViewSet

router = DefaultRouter()
router.register(r"chick-orders", ChickOrderViewSet, basename="chickorder")
router.register(r"reminders", ReminderViewSet, basename="reminder")

urlpatterns = [
    path("", include(router.urls)),
]
