# The monkey_patch call has been removed from here and is now handled conditionally in core/__init__.py
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Use environment variables for broker and backend, with fallback to localhost for development
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
backend_url = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

# Pass the broker and backend directly to the constructor for reliability on Windows.
app = Celery(
    'core',
    broker=broker_url,
    backend=backend_url
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

