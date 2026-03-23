#!/bin/bash
set -e

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn (use python -m to avoid PATH issues)
exec python -m gunicorn core.wsgi:application --bind 0.0.0.0:8000
