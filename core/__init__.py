import sys
import platform

# Auto-detect platform and pool type to apply appropriate monkey patching
# Only apply eventlet monkey patching when explicitly requested via -P eventlet
# This prevents conflicts with Redis connections when using prefork pool (default)
is_windows = platform.system() == 'Windows'
is_celery_worker = len(sys.argv) > 0 and 'celery' in sys.argv[0] and 'worker' in ' '.join(sys.argv)

# Check if eventlet is explicitly requested via command line
eventlet_requested = False
if is_celery_worker and len(sys.argv) > 1:
    cmd_line = ' '.join(sys.argv)
    # Check for -P eventlet or --pool eventlet
    if '-P eventlet' in cmd_line or '--pool=eventlet' in cmd_line or '--pool eventlet' in cmd_line:
        eventlet_requested = True

# Only apply eventlet monkey patching if explicitly requested
# Prefork pool (default) is more stable and doesn't need monkey patching
if is_celery_worker and eventlet_requested:
    try:
        import eventlet
        eventlet.monkey_patch()
        if is_windows:
            print("⚠ Warning: Using eventlet on Windows (explicitly requested)")
            print("  Note: Eventlet on Windows may have compatibility issues.")
            print("  For production, deploy on Linux/Mac for optimal performance.")
        else:
            print("✓ Eventlet monkey patching applied (explicitly requested via -P eventlet)")
    except ImportError:
        print("⚠ Error: Eventlet was requested but not installed.")
        print("  Install with: pip install eventlet")
        print("  Or use default prefork pool: celery -A core worker -l info")
        pass  # eventlet not installed, fall back to default pool
elif is_celery_worker:
    # Default: no monkey patching (works with prefork, solo, threads, gevent pools)
    pool_type = "prefork"
    if is_windows:
        pool_type = "solo"
    print(f"ℹ Using {pool_type} pool (default, no monkey patching)")
    print("  For eventlet, explicitly use: celery -A core worker -l info -P eventlet")

from .celery import app as celery_app

__all__ = ('celery_app',)

