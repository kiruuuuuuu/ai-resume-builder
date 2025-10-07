import sys
import eventlet

is_celery_worker = sys.argv and 'celery' in sys.argv[0] and 'worker' in sys.argv

if is_celery_worker:
    eventlet.monkey_patch()

from .celery import app as celery_app

__all__ = ('celery_app',)

