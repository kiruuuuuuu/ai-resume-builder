import sys
import platform

# Auto-detect platform and pool type to apply appropriate monkey patching
# Windows: Use 'solo' pool by default, but allow eventlet if explicitly requested
# Linux/Mac (Production): Use 'eventlet' for better concurrency
is_windows = platform.system() == 'Windows'
is_celery_worker = len(sys.argv) > 0 and 'celery' in sys.argv[0] and 'worker' in ' '.join(sys.argv)

# Check if eventlet is explicitly requested via command line
eventlet_requested = False
if is_celery_worker and len(sys.argv) > 1:
    cmd_line = ' '.join(sys.argv)
    # Check for -P eventlet or --pool eventlet
    if '-P eventlet' in cmd_line or '--pool=eventlet' in cmd_line or '--pool eventlet' in cmd_line:
        eventlet_requested = True

# Apply eventlet monkey patching if:
# 1. Not on Windows (production), OR
# 2. On Windows but explicitly requested with -P eventlet
if is_celery_worker and (not is_windows or eventlet_requested):
    try:
        import eventlet
        eventlet.monkey_patch()
        if is_windows and eventlet_requested:
            print("⚠ Warning: Using eventlet on Windows (explicitly requested)")
            print("  Note: Eventlet on Windows may have compatibility issues.")
            print("  For production, deploy on Linux/Mac for optimal performance.")
        else:
            print("✓ Eventlet monkey patching applied (Linux/Mac production mode)")
    except ImportError:
        print("⚠ Warning: eventlet not installed. Install with: pip install eventlet")
        if eventlet_requested:
            print("  Error: Eventlet was requested but not installed. Install eventlet or use -P solo instead.")
        else:
            print("  Falling back to default pool. For production, use: pip install eventlet")
        pass  # eventlet not installed, use default pool
elif is_celery_worker and is_windows and not eventlet_requested:
    # Windows default - no eventlet
    print("ℹ Running on Windows: Using solo pool (recommended for Windows)")
    print("  To test eventlet on Windows, use: celery -A core worker -l info -P eventlet")

from .celery import app as celery_app

__all__ = ('celery_app',)

