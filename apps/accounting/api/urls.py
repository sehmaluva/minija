from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, CostViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r"sales", SaleViewSet)
router.register(r"costs", CostViewSet)
router.register(r"transactions", TransactionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
