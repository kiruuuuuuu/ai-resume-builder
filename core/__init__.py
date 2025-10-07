import sys
import eventlet

# --- THE FINAL FIX IS HERE ---
# This code checks if the process was started as a Celery worker.
# If so, it applies the eventlet patch. Otherwise, it does nothing.
# This isolates the patch to ONLY the Celery worker, fixing both the worker
# shutdown crash and the Django server startup crash.
is_celery_worker = sys.argv and 'celery' in sys.argv[0] and 'worker' in sys.argv

if is_celery_worker:
    eventlet.monkey_patch()

from .celery import app as celery_app

__all__ = ('celery_app',)

