"""
Django management command to create a superuser from environment variables.
This is useful for deployment platforms like Railway where terminal access is limited.

Usage:
    python manage.py create_superuser_from_env

Environment Variables:
    DJANGO_SUPERUSER_USERNAME - Username for the superuser
    DJANGO_SUPERUSER_EMAIL - Email for the superuser
    DJANGO_SUPERUSER_PASSWORD - Password for the superuser

Example:
    export DJANGO_SUPERUSER_USERNAME=admin
    export DJANGO_SUPERUSER_EMAIL=admin@example.com
    export DJANGO_SUPERUSER_PASSWORD=securepassword123
    python manage.py create_superuser_from_env
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser from environment variables'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Checking for superuser creation ===')
        )
        
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not username:
            self.stdout.write(
                self.style.WARNING(
                    'DJANGO_SUPERUSER_USERNAME not set. Skipping superuser creation.'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'To create a superuser, set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD environment variables.'
                )
            )
            return

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    'DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'To create a superuser, set DJANGO_SUPERUSER_PASSWORD environment variable.'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Environment variables found. Attempting to create superuser: {username}'
            )
        )

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(
                        f'Superuser "{username}" already exists. Skipping creation.'
                    )
                )
                return
            else:
                # Update existing user to superuser
                user.is_superuser = True
                user.is_staff = True
                user.email = email
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Existing user "{username}" has been upgraded to superuser.'
                    )
                )
                return

        # Create new superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser "{username}"'
                )
            )
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(
                    f'Error: User "{username}" already exists.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating superuser: {str(e)}'
                )
            )

