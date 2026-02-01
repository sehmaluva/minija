"""
Django settings for core project.
"""

import os
from pathlib import Path
from decouple import config

# Timezone and Language choices
from apps.account.timezones import TIMEZONES
from apps.account.languages import LANGUAGES

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

INSTALLED_APPS = [
    # django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # third party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_extensions",
    "apps.account",
    "apps.health",
    "apps.birds",
    "apps.production",
    "apps.reports",
    "apps.users",
    "apps.accounting",
    "apps.orders",
    "apps.forecast",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Harare"
USE_I18N = True
# USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# ==================== ACCOUNT APP SETTINGS ====================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025  # Mailpit SMTP port
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "noreply@minija.com"

# URL Names for email links
ACCOUNT_EMAIL_CONFIRMATION_URL = (
    "account_confirm_email"  # URL name for email confirmation
)
ACCOUNT_PASSWORD_RESET_TOKEN_URL = (
    "account_password_reset_confirm"  # URL name for password reset
)

# Hookset Configuration
ACCOUNT_HOOKSET = "apps.account.hooks.AccountDefaultHookSet"

# Signup Settings
ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_APPROVAL_REQUIRED = False

# Email Settings
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = (
    False  # Set True to require email verification before login
)
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_CONFIRMATION_AUTO_LOGIN = False
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = None
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = None

# Password Settings
ACCOUNT_PASSWORD_USE_HISTORY = True
ACCOUNT_PASSWORD_EXPIRY = 0  # 0 = never expire, or seconds
ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE = True
ACCOUNT_PASSWORD_STRIP = True

# Session Settings
ACCOUNT_REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 365 * 10  # 10 years

# Deletion Settings
ACCOUNT_DELETION_EXPUNGE_HOURS = 48

# Redirect URLs (for non-API use)
ACCOUNT_LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_SIGNUP_REDIRECT_URL = "/dashboard/"
ACCOUNT_PASSWORD_RESET_REDIRECT_URL = "/login/"
ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = "/settings/"
ACCOUNT_SETTINGS_REDIRECT_URL = "/settings/"

# Protocol
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"  # Change to "https" in production


ACCOUNT_TIMEZONES = TIMEZONES
ACCOUNT_LANGUAGES = LANGUAGES


# Sites Framework
SITE_ID = 1
# =============================================================

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

# Spectacular settings for API documentation
SPECTACULAR_SETTINGS = {
    "TITLE": "Poultry Management API",
    "DESCRIPTION": "A comprehensive API for managing broilers, including production tracking, health monitoring, accounting, orders, and forecasting",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {
        "name": "API Support",
        "email": "sehmaluva@gmail.com",
    },
    "LICENSE": {
        "name": "Apache 3.0",
    },
    "SCHEMA_PATH_PREFIX": "/api",
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": True,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": None,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "filter": True,
        "tryItOutEnabled": True,
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
    },
    "SWAGGER_UI_FAVICON_HREF": None,
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": False,
        "expandResponses": "200,201",
        "pathInMiddlePanel": True,
    },
    "PREPROCESSING_HOOKS": [],
    "POSTPROCESSING_HOOKS": [],
    "ENUM_NAME_OVERRIDES": {},
    "TAGS": [
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints",
        },
        {"name": "Batch", "description": "Batch management operations"},
        {"name": "Production", "description": "Egg production tracking"},
        {"name": "Health", "description": "Health monitoring and management"},
        {"name": "Accounting", "description": "Financial transactions and accounting"},
        {"name": "Orders", "description": "Order management"},
        {"name": "Forecast", "description": "Production forecasting"},
        {"name": "Reports", "description": "Reports and analytics"},
    ],
}

# Django default task handler
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.database.DatabaseBackend",
    }
}


# Celery Configuration (for background tasks)
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Custom user model
AUTH_USER_MODEL = "users.User"

# JWT Settings
from datetime import timedelta
from typing import Any, Dict

SIMPLE_JWT: Dict[str, Any] = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# Logging configuration
LOGS_DIR = os.path.join(BASE_DIR, "core", "logs")
LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(LOGS_DIR, "django.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Dynamically create a handler and logger for each custom app
for app_name in [app for app in INSTALLED_APPS if app.startswith("apps.")]:
    app_name_short = app_name.split(".")[-1]
    LOGGING["handlers"][f"{app_name_short}_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "standard",
        "filename": os.path.join(LOGS_DIR, f"{app_name_short}.log"),
        "maxBytes": 1024 * 1024 * 5,  # 5MB
        "backupCount": 5,
        "encoding": "utf8",
    }
    LOGGING["loggers"][app_name] = {
        "handlers": ["console", f"{app_name_short}_file"],
        "level": "DEBUG" if DEBUG else "INFO",
        "propagate": False,
    }

# Ensure logs directory exists in production/dev startup (best-effort)
try:
    os.makedirs(LOGS_DIR, exist_ok=True)
except Exception:
    pass
