#!/bin/bash
# Script to create superuser if environment variables are set
# This can be run during deployment or as a one-time setup

# Check if environment variables are set
if [ -z "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "DJANGO_SUPERUSER_USERNAME not set, skipping superuser creation"
    exit 0
fi

if [ -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "DJANGO_SUPERUSER_PASSWORD not set, skipping superuser creation"
    exit 0
fi

# Run the management command
python manage.py create_superuser_from_env

