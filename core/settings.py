"""
Django settings for core project.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


def getenv_required(key: str) -> str:
    """Get a required environment variable."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def getenv_bool(key: str, default: bool = False) -> bool:
    """Get a boolean environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def getenv_int(key: str, default: int = 0) -> int:
    """Get an integer environment variable."""
    value = os.getenv(key, str(default))
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Environment variable '{key}' must be an integer, got '{value}'"
        )


def getenv_list(key: str, default: str = "") -> list[str]:
    """Get a list environment variable (comma-separated)."""
    value = os.getenv(key, default)
    return [item.strip() for item in value.split(",") if item.strip()]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv_required("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv_bool("DEBUG")

ALLOWED_HOSTS = getenv_list("ALLOWED_HOSTS", "localhost,127.0.0.1")

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

INSTALLED_APPS = [
    # django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_extensions",
    # local apps
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
    "apps.users.middleware.OrganizationMiddleware",
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
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": getenv_int("DB_PORT", 5432),
    }
}

# Use SQLite in-memory for tests (avoids CREATEDB permission requirement)
if "test" in sys.argv or "test_coverage" in sys.argv:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
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


# ==================== EMAIL SETTINGS ====================
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = getenv_int("EMAIL_PORT", 587)
EMAIL_USE_TLS = getenv_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = getenv_bool("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# ==================== OTP SETTINGS ====================
OTP_LENGTH = getenv_int("OTP_LENGTH", 6)
OTP_EXPIRY_MINUTES = getenv_int("OTP_EXPIRY_MINUTES", 10)
OTP_MAX_ATTEMPTS = getenv_int("OTP_MAX_ATTEMPTS", 3)
OTP_RESEND_COOLDOWN_SECONDS = getenv_int("OTP_RESEND_COOLDOWN_SECONDS", 60)

# ==================== ORGANIZATION SETTINGS ====================
ORGANIZATION_INVITATION_EXPIRY_DAYS = getenv_int(
    "ORGANIZATION_INVITATION_EXPIRY_DAYS", 7
)
ORGANIZATION_MEMBER_LIMIT = getenv_int("ORGANIZATION_MEMBER_LIMIT", 10)

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
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
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
    # "TAGS": [
    #     {
    #         "name": "Authentication",
    #         "description": "User authentication and authorization endpoints",
    #     },
    #     {"name": "Batch", "description": "Batch management operations"},
    #     {"name": "Production", "description": "Egg production tracking"},
    #     {"name": "Health", "description": "Health monitoring and management"},
    #     {"name": "Accounting", "description": "Financial transactions and accounting"},
    #     {"name": "Orders", "description": "Order management"},
    #     {"name": "Forecast", "description": "Production forecasting"},
    #     {"name": "Reports", "description": "Reports and analytics"},
    # ],
}

# Django default task handler
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.database.DatabaseBackend",
    }
}


# Celery Configuration (for background tasks)
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
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
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,  # Disabled for performance - eliminates extra DB write
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
