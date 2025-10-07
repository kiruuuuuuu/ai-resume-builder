# The monkey_patch call has been removed from here and is now handled conditionally in core/__init__.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Pass the broker and backend directly to the constructor for reliability on Windows.
app = Celery(
    'core',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0'
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

