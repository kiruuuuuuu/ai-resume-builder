from jobs.models import Notification
from django.conf import settings

def notifications(request):
        if request.user.is_authenticated and request.user.user_type == 'employer':
            unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
            return {
                'notifications': unread_notifications,
                'notification_count': unread_notifications.count()
            }
        return {}

def jobs_feature_enabled(request):
    """Make JOBS_FEATURE_ENABLED setting available in all templates."""
    return {
        'JOBS_FEATURE_ENABLED': getattr(settings, 'JOBS_FEATURE_ENABLED', False)
    }
