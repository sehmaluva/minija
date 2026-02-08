from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, CostViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r"sales", SaleViewSet, basename="sale")
router.register(r"costs", CostViewSet, basename="cost")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
]
