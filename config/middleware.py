from django.contrib.auth import logout
from django.utils import timezone
from social.models import DeviceSession
from profiles.models import Profile


class SingleDeviceMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        if request.user.is_authenticated:
            try:
                Profile.objects.filter(user=request.user).update(last_seen=timezone.now())
                d=DeviceSession.objects.get(user=request.user)
                token=request.COOKIES.get('nexora_device')
                if d.expires_at<=timezone.now() or d.session_key!=request.session.session_key or not token or token!=d.device_token:
                    logout(request)
            except DeviceSession.DoesNotExist: pass
        return self.get_response(request)
