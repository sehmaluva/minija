"""API URL configurations for User Accounts management"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.account.api.views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    ConfirmEmailAPIView,
    ChangePasswordAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    AccountSettingsAPIView,
    AccountDeleteAPIView,
    ResendEmailVerificationAPIView,
)

urlpatterns = [
    # Authentication
    path("register/", RegisterAPIView.as_view(), name="account_register"),
    path("login/", LoginAPIView.as_view(), name="account_login"),
    path("logout/", LogoutAPIView.as_view(), name="account_logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Email verification
    path(
        "confirm-email/<str:key>/",
        ConfirmEmailAPIView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "confirm-email/",
        ConfirmEmailAPIView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "resend-verification/",
        ResendEmailVerificationAPIView.as_view(),
        name="account_resend_verification",
    ),
    # Password management
    path(
        "password/change/",
        ChangePasswordAPIView.as_view(),
        name="account_password_change",
    ),
    path(
        "password/reset/",
        PasswordResetRequestAPIView.as_view(),
        name="account_password_reset",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmAPIView.as_view(),
        name="account_password_reset_confirm",
    ),
    # Account settings
    path("settings/", AccountSettingsAPIView.as_view(), name="account_settings"),
    # Account deletion
    path("delete/", AccountDeleteAPIView.as_view(), name="account_delete"),
]
