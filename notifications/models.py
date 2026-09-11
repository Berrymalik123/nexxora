from django.conf import settings
from django.db import models
class Notification(models.Model):
    TYPES=[('follow','Follow'),('like','Like'),('comment','Comment'),('share','Share'),('story','Story')]
    recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications')
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='sent_notifications')
    notification_type=models.CharField(max_length=20,choices=TYPES)
    text=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)
    class Meta: ordering=['-created_at']
