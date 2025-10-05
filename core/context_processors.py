from jobs.models import Notification

def notifications(request):
        if request.user.is_authenticated and request.user.user_type == 'employer':
            unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
            return {
                'notifications': unread_notifications,
                'notification_count': unread_notifications.count()
            }
        return {}
