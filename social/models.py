from django.conf import settings
from django.db import models

class Story(models.Model):
    STORY_TYPES = [('media','Media'),('text','Text')]
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    media = models.FileField(upload_to='stories/', blank=True, null=True)
    text = models.TextField(blank=True, max_length=1000)
    story_type = models.CharField(max_length=10, choices=STORY_TYPES, default='media')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    class Meta: ordering=['-created_at']

class StorySeen(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='seen_by')
    seen_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together=('user','story')

class Report(models.Model):
    REASONS=[('spam','Spam'),('abuse','Abuse'),('copyright','Copyright'),('unsafe','Unsafe content'),('other','Other')]
    reporter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='reports_made')
    post=models.ForeignKey('posts.Post',null=True,blank=True,on_delete=models.CASCADE,related_name='reports')
    reel=models.ForeignKey('posts.Reel',null=True,blank=True,on_delete=models.CASCADE,related_name='reports')
    reason=models.CharField(max_length=20,choices=REASONS,default='other')
    details=models.TextField(blank=True,max_length=500)
    created_at=models.DateTimeField(auto_now_add=True)
    resolved=models.BooleanField(default=False)
    class Meta: ordering=['-created_at']

class ContentView(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    post=models.ForeignKey('posts.Post',null=True,blank=True,on_delete=models.CASCADE,related_name='content_views')
    reel=models.ForeignKey('posts.Reel',null=True,blank=True,on_delete=models.CASCADE,related_name='content_views')
    session_key=models.CharField(max_length=100,blank=True,default='')
    viewed_at=models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='sent_messages')
    recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='received_messages')
    text=models.TextField(max_length=2000)
    image=models.ImageField(upload_to='messages/images/',blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)
    class Meta: ordering=['created_at']

class DeviceSession(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='device_session')
    device_token=models.CharField(max_length=128,unique=True)
    session_key=models.CharField(max_length=100,blank=True)
    last_seen=models.DateTimeField(auto_now=True)
    expires_at=models.DateTimeField()

class TwoFactorCode(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='two_factor_code')
    code_hash=models.CharField(max_length=128)
    expires_at=models.DateTimeField()
    attempts=models.PositiveIntegerField(default=0)
