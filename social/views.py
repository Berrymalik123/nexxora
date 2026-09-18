import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from posts.models import Post, Reel
from .models import Report, Message, CallSession
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
        text=(request.POST.get('text') or '').strip()[:2000]; image=request.FILES.get('image'); audio=request.FILES.get('audio'); one_time=request.POST.get('one_time')=='on'
        if image and image.size>10*1024*1024: return JsonResponse({'ok':False,'error':'Images must be 10 MB or smaller.'},status=400)
        if image and not (image.content_type or '').startswith('image/'): return JsonResponse({'ok':False,'error':'Only image files are allowed.'},status=400)
        if audio and audio.size == 0: return JsonResponse({'ok':False,'error':'The voice recording is empty. Please record again.'},status=400)
        if audio and audio.size>20*1024*1024: return JsonResponse({'ok':False,'error':'Voice messages must be 20 MB or smaller.'},status=400)
        if audio and not (audio.content_type or '').startswith('audio/'): return JsonResponse({'ok':False,'error':'Only audio files are allowed.'},status=400)
        if not text and not image and not audio: return JsonResponse({'ok':False,'error':'Write a message, choose an image, or record a voice message.'},status=400)
        Message.objects.create(sender=request.user,recipient=other,text=text,image=image,audio=audio,one_time=one_time)
        return JsonResponse({'ok':True}) if request.headers.get('x-requested-with')=='XMLHttpRequest' else render(request,'social/conversation.html',{'other':other,'messages':Message.objects.filter(sender__in=[request.user,other],recipient__in=[request.user,other]).select_related('sender','reel')})
    Message.objects.filter(sender=other,recipient=request.user,is_read=False).update(is_read=True)
    msgs=Message.objects.filter(sender__in=[request.user,other],recipient__in=[request.user,other]).exclude(one_time=True,opened_at__isnull=False).select_related('sender','reel')
    return render(request,'social/conversation.html',{'other':other,'messages':msgs})

@login_required
def call_signal(request, username):
    User=get_user_model(); other=get_object_or_404(User, username=username)
    if request.method == 'GET':
        calls=CallSession.objects.filter(status__in=['ringing','connected']).filter(Q(caller=request.user,recipient=other)|Q(caller=other,recipient=request.user)).order_by('-updated_at')[:5]
        return JsonResponse({'calls':[{'id':c.id,'caller':c.caller_id,'kind':c.kind,'status':c.status,'offer':c.offer,'answer':c.answer,'caller_candidates':c.caller_candidates,'recipient_candidates':c.recipient_candidates} for c in calls]})
    data=json.loads(request.body or '{}')
    action=data.get('action'); call_id=data.get('call_id')
    if action=='start':
        call=CallSession.objects.create(caller=request.user,recipient=other,kind=data.get('kind','voice'),offer=data.get('offer',{}))
    else:
        call=get_object_or_404(CallSession, id=call_id)
        if request.user not in (call.caller,call.recipient): return JsonResponse({'error':'Not allowed'},status=403)
        if action=='answer': call.answer=data.get('answer',{}); call.status='connected'
        elif action=='candidate':
            field='caller_candidates' if request.user==call.caller else 'recipient_candidates'; values=getattr(call,field); values.append(data.get('candidate')); setattr(call,field,values)
        elif action=='end': call.status='ended'
    call.save()
    return JsonResponse({'ok':True,'call_id':call.id,'status':call.status})

@login_required
def open_one_time_message(request,message_id):
    if request.method != 'POST': return JsonResponse({'ok':False,'error':'POST required'},status=405)
    message=get_object_or_404(Message,id=message_id,recipient=request.user,one_time=True,opened_at__isnull=True)
    message.opened_at=timezone.now(); message.save(update_fields=['opened_at'])
    return JsonResponse({'ok':True})

@login_required
def share_reel_message(request,reel_id):
    if request.method != 'POST': return JsonResponse({'ok':False,'error':'POST required'},status=405)
    reel=get_object_or_404(Reel,id=reel_id)
    from django.contrib.auth import get_user_model
    User=get_user_model()
    usernames=list(dict.fromkeys(request.POST.getlist('usernames')))
    friends=User.objects.filter(username__in=usernames).exclude(pk=request.user.pk)
    if not friends.exists(): return JsonResponse({'ok':False,'error':'Choose at least one friend.'},status=400)
    text=(request.POST.get('text') or '').strip()[:500]
    Message.objects.bulk_create([Message(sender=request.user,recipient=friend,reel=reel,text=text) for friend in friends])
    names=', '.join(f'@{friend.username}' for friend in friends)
    return JsonResponse({'ok':True,'message':f'Reel sent to {names}.'})
