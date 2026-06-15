from model_share.models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {'unread_count': unread_count, 'notifications': notifications}
    return {'unread_count': 0, 'notifications': []}
