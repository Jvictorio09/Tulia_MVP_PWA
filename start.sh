#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput || echo "Migrations failed, continuing..."

echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static files collection failed, continuing..."

echo "Starting Gunicorn..."
exec gunicorn myProject.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile -

