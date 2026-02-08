"""
WSGI config for core project.
"""

import os
import email.charset  # noqa: E402 — Python 3.12 import deadlock workaround
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
