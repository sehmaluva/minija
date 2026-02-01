"""
URL configuration for core project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API endpoints
    path("api/account/", include("apps.account.api.urls")),
    path("api/auth/", include("apps.users.api.urls")),
    # Removed farms/health API includes for broiler-focused product
    path("api/birds/", include("apps.birds.api.urls")),
    path("api/accounting/", include("apps.accounting.api.urls")),
    path("api/orders/", include("apps.orders.api.urls")),
    path("api/forecast/", include("apps.forecast.api.urls")),
    path("api/production/", include("apps.production.api.urls")),
    path("api/reports/", include("apps.reports.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
