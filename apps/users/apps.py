from django.apps import AppConfig
from django.contrib.admin import sites
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """Configuration for the Users app.

    Args:
        AppConfig (_type_): _description_
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    label = "users"
    verbose_name = _("User Management")

    def ready(self):
        sites.AdminSite.site_header = _("HukuMan Administration")
        sites.AdminSite.site_title = _("HukuMan Admin Portal")
        sites.AdminSite.index_title = _("Welcome to HukuMan Admin")
