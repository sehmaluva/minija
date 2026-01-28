"""URLS for User Management App"""

from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("permissions/", views.user_permissions_view, name="user_permissions"),
    path("verify-email/", views.EmailVerificationView.as_view(), name="email_verify"),
    path(
        "resend-verification/",
        views.ResendVerificationEmailView.as_view(),
        name="resend_verification",
    ),
]
