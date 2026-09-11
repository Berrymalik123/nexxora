from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from posts.models import Post, Reel
from .models import Report, Message
@login_required
def report_content(request,kind,object_id):
    if request.method!='POST': return JsonResponse({'ok':False,'error':'POST required'},status=405)
    post=get_object_or_404(Post,id=object_id) if kind=='post' else None; reel=get_object_or_404(Reel,id=object_id) if kind=='reel' else None
    if kind not in ('post','reel'): return JsonResponse({'ok':False,'error':'Invalid content'},status=400)
    reason=request.POST.get('reason','other'); reason=reason if reason in dict(Report.REASONS) else 'other'
    Report.objects.create(reporter=request.user,post=post,reel=reel,reason=reason,details=request.POST.get('details','')[:500]); return JsonResponse({'ok':True,'message':'Report submitted.'})
@login_required
def inbox(request):
    users=request.user.sent_messages.values_list('recipient',flat=True)
    recipients=request.user.received_messages.values_list('sender',flat=True)
    ids=set(users)|set(recipients); from django.contrib.auth import get_user_model; User=get_user_model(); people=User.objects.filter(id__in=ids).select_related('profile').order_by('username')
    return render(request,'social/inbox.html',{'people':people,'unread_total':Message.objects.filter(recipient=request.user,is_read=False).count()})
@login_required
def conversation(request,username):
    from django.contrib.auth import get_user_model; User=get_user_model(); other=get_object_or_404(User,username=username)
    if request.method=='POST':
        text=(request.POST.get('text') or '').strip()[:2000]; image=request.FILES.get('image')
        if image and image.size>10*1024*1024: return JsonResponse({'ok':False,'error':'Images must be 10 MB or smaller.'},status=400)
        if image and not (image.content_type or '').startswith('image/'): return JsonResponse({'ok':False,'error':'Only image files are allowed.'},status=400)
        if not text and not image: return JsonResponse({'ok':False,'error':'Write a message or choose an image.'},status=400)
        Message.objects.create(sender=request.user,recipient=other,text=text,image=image)
        return JsonResponse({'ok':True}) if request.headers.get('x-requested-with')=='XMLHttpRequest' else render(request,'social/conversation.html',{'other':other,'messages':Message.objects.filter(sender__in=[request.user,other],recipient__in=[request.user,other]).select_related('sender')})
    Message.objects.filter(sender=other,recipient=request.user,is_read=False).update(is_read=True)
    msgs=Message.objects.filter(sender__in=[request.user,other],recipient__in=[request.user,other]).select_related('sender')
    return render(request,'social/conversation.html',{'other':other,'messages':msgs})
