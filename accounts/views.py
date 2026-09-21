import hashlib,secrets
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.shortcuts import redirect,render
from django.db import transaction
from django.utils import timezone
from social.models import TwoFactorCode,DeviceSession
from .forms import RegisterForm
User=get_user_model()

def _code_hash(code): return hashlib.sha256((settings.SECRET_KEY+code).encode()).hexdigest()
def _device_token(request): return request.COOKIES.get('nexora_device') or secrets.token_urlsafe(48)
def _finish_login(request,user,token):
    # OneToOne DeviceSession replaces the previous active device immediately.
    login(request,user); request.session.set_expiry(60*24*60*60); request.session.save()
    with transaction.atomic():
        DeviceSession.objects.filter(device_token=token).exclude(user=user).delete()
        DeviceSession.objects.update_or_create(user=user,defaults={'device_token':token,'session_key':request.session.session_key,'expires_at':timezone.now()+timedelta(days=60)})

def login_view(request):
    if request.user.is_authenticated: return redirect('home')
    form=AuthenticationForm(request,data=request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.get_user(); token=_device_token(request); _finish_login(request,user,token)
        response=redirect('home'); response.set_cookie('nexora_device',token,max_age=60*24*60*60,httponly=True,samesite='Lax'); return response
    return render(request,'accounts/login.html',{'form':form})

def verify_2fa(request):
    uid=request.session.get('pending_2fa_user')
    if not uid: return redirect('login')
    user=User.objects.filter(pk=uid).first()
    if not user: return redirect('login')
    if request.method=='POST':
        code=(request.POST.get('code') or '').strip(); rec=TwoFactorCode.objects.filter(user=user).first()
        if rec and rec.attempts<5 and rec.expires_at>timezone.now() and secrets.compare_digest(rec.code_hash,_code_hash(code)):
            token=request.session.get('pending_device_token') or _device_token(request); _finish_login(request,user,token); rec.delete(); request.session.pop('pending_2fa_user',None); request.session.pop('pending_device_token',None); request.session.pop('dev_2fa_code',None)
            resp=redirect('home'); resp.set_cookie('nexora_device',token,max_age=60*24*60*60,httponly=True,samesite='Lax'); return resp
        if rec: rec.attempts+=1; rec.save(update_fields=['attempts'])
        messages.error(request,'Invalid or expired verification code.')
    return render(request,'accounts/verify_2fa.html',{'dev_code':request.session.get('dev_2fa_code')})

def register_view(request):
    if request.user.is_authenticated:return redirect('home')
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): user=form.save(); messages.success(request,'Account created. Please log in and verify your code.'); return redirect('login')
    return render(request,'accounts/register.html',{'form':form})
def logout_view(request): logout(request); return redirect('login')
