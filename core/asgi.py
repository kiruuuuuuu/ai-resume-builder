"""
ASGI config for core project.
"""
# The eventlet patch has been removed from this file.
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_asgi_application()

