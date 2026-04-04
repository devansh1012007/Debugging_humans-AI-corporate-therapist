#!/bin/bash
set -e

echo "Starting deployment sequence..."

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
# Replace 'backend_AI_Corporate_therapist' if your wsgi.py folder is named differently
# Force verbose logging to expose the exact failure point
exec gunicorn backend_AI_Corporate_therapist.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --log-level debug --capture-output