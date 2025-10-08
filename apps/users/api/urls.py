from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path(
        "token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("permissions/", views.user_permissions_view, name="user_permissions"),
]
