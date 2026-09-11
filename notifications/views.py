from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import Notification
@login_required
def notifications_view(request):
    notifications=Notification.objects.filter(recipient=request.user).select_related('actor')
    return render(request,'notifications/notifications.html',{'notifications':notifications,'unread_count':notifications.filter(is_read=False).count()})
@login_required
def mark_read(request,notification_id=None):
    qs=Notification.objects.filter(recipient=request.user,is_read=False)
    if notification_id: qs=qs.filter(id=notification_id)
    count=qs.update(is_read=True); return JsonResponse({'ok':True,'count':count})
