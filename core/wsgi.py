"""
WSGI config for core project.
"""
# The eventlet patch has been removed from this file.
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

