"""
Decorator to block job-related features when JOBS_FEATURE_ENABLED is False.
Shows a "Coming Soon" page instead of the actual content.
"""
from functools import wraps
from django.conf import settings
from django.shortcuts import render


def job_feature_disabled(view_func):
    """
    Decorator that checks if job features are enabled.
    If disabled, shows a "Coming Soon" template instead of the actual view.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if job features are enabled
        if not getattr(settings, 'JOBS_FEATURE_ENABLED', False):
            # Render the coming soon template
            return render(request, 'jobs/coming_soon.html')
        
        # If enabled, proceed with the original view
        return view_func(request, *args, **kwargs)
    
    return wrapper

