#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Workaround for Python 3.12 import deadlock: SimpleJWT's settings.py imports
# from django.test.signals which triggers loading django.test.testcases during
# apps.populate(), causing an import lock deadlock via email.charset.
# Pre-import the email submodules to break the deadlock cycle.
# import email.charset  # noqa: E402

if __name__ == "__main__":
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
