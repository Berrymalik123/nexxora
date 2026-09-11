import json, os, re, secrets, subprocess, tempfile
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from .forms import PostForm, ReelForm
from .models import Comment, Like, Save, Share, Post, Reel, ReelLike, ReelSave, ReelShare, ReelComment, Hashtag
from notifications.models import Notification
from social.models import ContentView, Story, StorySeen
User=get_user_model()

def wants_json(request): return request.headers.get('x-requested-with')=='XMLHttpRequest' or request.headers.get('accept','').startswith('application/json')
def ok(**data): return JsonResponse({'ok':True,**data})

def _hashtags(text): return {x.lower() for x in re.findall(r'#([A-Za-z0-9_]+)', text or '')}
def _sync_hashtags(obj,text,is_reel=False):
    for name in _hashtags(text):
        tag,_=Hashtag.objects.get_or_create(name=name[:80])
        (tag.reels if is_reel else tag.posts).add(obj)

def _notify(recipient, actor, kind, text):
    if recipient != actor: Notification.objects.create(recipient=recipient, actor=actor, notification_type=kind, text=text)

def _render_post_cards(request, posts):
    return render(request,'posts/_post_cards.html',{'posts':posts,'user':request.user}).content.decode()

@ensure_csrf_cookie
def home(request):
    qs=Post.objects.filter(is_public=True).select_related('author','author__profile').prefetch_related('likes','saves','comments__user','hashtags').order_by('-created_at')
    page=Paginator(qs,8).get_page(request.GET.get('page',1)); posts=page.object_list
    reels=Reel.objects.select_related('author','author__profile').prefetch_related('likes','saves','comments')[:10]
    stories=Story.objects.filter(expires_at__gt=timezone.now()).select_related('author','author__profile')[:30]
    liked_posts=saved_posts=liked_reels=saved_reels=seen_stories=set()
    if request.user.is_authenticated:
        liked_posts=set(Like.objects.filter(user=request.user,post__in=posts).values_list('post_id',flat=True))
        saved_posts=set(Save.objects.filter(user=request.user,post__in=posts).values_list('post_id',flat=True))
        liked_reels=set(ReelLike.objects.filter(user=request.user,reel__in=reels).values_list('reel_id',flat=True))
        saved_reels=set(ReelSave.objects.filter(user=request.user,reel__in=reels).values_list('reel_id',flat=True))
        seen_stories=set(StorySeen.objects.filter(user=request.user,story__in=stories).values_list('story_id',flat=True))
    ctx={'posts':posts,'reels':reels,'stories':stories,'liked_post_ids':liked_posts,'saved_post_ids':saved_posts,'liked_reel_ids':liked_reels,'saved_reel_ids':saved_reels,'seen_story_ids':seen_stories,'has_next':page.has_next()}
    if wants_json(request): return JsonResponse({'ok':True,'html':_render_post_cards(request,posts),'has_next':page.has_next(),'page':page.number})
    return render(request,'posts/home.html',ctx)

@login_required
@ensure_csrf_cookie
def videos(request):
    posts=Post.objects.filter(video__isnull=False,is_public=True).select_related('author','author__profile').prefetch_related('likes','saves','comments').order_by('-created_at')
    liked=set(Like.objects.filter(user=request.user,post__in=posts).values_list('post_id',flat=True)); saved=set(Save.objects.filter(user=request.user,post__in=posts).values_list('post_id',flat=True))
    return render(request,'posts/videos.html',{'video_posts':posts,'liked_post_ids':liked,'saved_post_ids':saved})

@login_required
@ensure_csrf_cookie
def reels(request):
    reels_qs=Reel.objects.select_related('author','author__profile').prefetch_related('likes','saves','comments').order_by('-created_at')
    liked=set(ReelLike.objects.filter(user=request.user,reel__in=reels_qs).values_list('reel_id',flat=True)); saved=set(ReelSave.objects.filter(user=request.user,reel__in=reels_qs).values_list('reel_id',flat=True))
    return render(request,'posts/reels.html',{'reels':reels_qs,'liked_reel_ids':liked,'saved_reel_ids':saved})

@login_required
def create_post(request):
    form=PostForm(request.POST or None,request.FILES or None)
    if request.method=='POST' and form.is_valid():
        p=form.save(commit=False); p.author=request.user
        upload=p.video or p.image
        if upload and getattr(upload,'size',0)>100*1024*1024: form.add_error(None,'Maximum upload size is 100 MB.')
        else:
            p.save(); _sync_hashtags(p,p.content); return redirect('home')
    return render(request,'posts/create_post.html',{'form':form})

@login_required
def create_reel(request):
    form=ReelForm(request.POST or None,request.FILES or None)
    if request.method=='POST' and form.is_valid():
        r=form.save(commit=False); r.author=request.user
        if getattr(r.video,'size',0)>100*1024*1024: form.add_error('video','Maximum reel size is 100 MB.')
        else:
            r.save(); _sync_hashtags(r,r.caption,True); return redirect('reels')
    return render(request,'posts/create_reel.html',{'form':form})

@login_required
def add_story(request):
    if request.method!='POST': return JsonResponse({'ok':False,'error':'POST required'},status=405)
    media=request.FILES.get('media'); text=(request.POST.get('text') or '').strip()
    if not media and not text: return JsonResponse({'ok':False,'error':'Add text or media.'},status=400)
    if media and media.size>50*1024*1024: return JsonResponse({'ok':False,'error':'Story media must be under 50 MB.'},status=400)
    s=Story.objects.create(author=request.user,media=media,text=text,story_type='media' if media else 'text',expires_at=timezone.now()+timedelta(hours=24))
    return ok(id=s.id)

@login_required
def seen_story(request,story_id):
    s=get_object_or_404(Story,id=story_id)
    StorySeen.objects.get_or_create(user=request.user,story=s)
    return ok()

def _toggle_unique(model,user,field_name,obj):
    kwargs={'user':user,field_name:obj}; existing=model.objects.filter(**kwargs).first()
    if existing: existing.delete(); return False, model.objects.filter(**{field_name:obj}).count()
    model.objects.create(**kwargs); return True, model.objects.filter(**{field_name:obj}).count()

@login_required
def like_post(request,post_id):
    p=get_object_or_404(Post,id=post_id); liked,count=_toggle_unique(Like,request.user,'post',p)
    if liked: _notify(p.author,request.user,'like',f'@{request.user.username} liked your post.')
    return ok(liked=liked,count=count)
@login_required
def like_reel(request,reel_id):
    r=get_object_or_404(Reel,id=reel_id); liked,count=_toggle_unique(ReelLike,request.user,'reel',r)
    if liked: _notify(r.author,request.user,'like',f'@{request.user.username} liked your reel.')
    return ok(liked=liked,count=count)
@login_required
def save_post(request,post_id):
    p=get_object_or_404(Post,id=post_id); saved,count=_toggle_unique(Save,request.user,'post',p); return ok(saved=saved,count=count)
@login_required
def save_reel(request,reel_id):
    r=get_object_or_404(Reel,id=reel_id); saved,count=_toggle_unique(ReelSave,request.user,'reel',r); return ok(saved=saved,count=count)
@login_required
def share_post(request,post_id):
    if request.method!='POST': return JsonResponse({'ok':False,'error':'POST required'},status=405)
    p=get_object_or_404(Post,id=post_id); Share.objects.create(user=request.user,post=p); _notify(p.author,request.user,'share',f'@{request.user.username} shared your post.'); return ok(count=p.shares.count())
@login_required
def share_reel(request,reel_id):
    if request.method!='POST': return JsonResponse({'ok':False,'error':'POST required'},status=405)
    r=get_object_or_404(Reel,id=reel_id); ReelShare.objects.create(user=request.user,reel=r); _notify(r.author,request.user,'share',f'@{request.user.username} shared your reel.'); return ok(count=r.shares.count())

@login_required
def add_comment(request,post_id):
    if request.method!='POST': return JsonResponse({'ok':False},status=405)
    p=get_object_or_404(Post,id=post_id); content=(request.POST.get('content') or '').strip()[:1000]
    if not content:return JsonResponse({'ok':False,'error':'Comment cannot be empty.'},status=400)
    c=Comment.objects.create(user=request.user,post=p,content=content); _notify(p.author,request.user,'comment',f'@{request.user.username} commented on your post.')
    return ok(id=c.id,username=request.user.username,content=c.content,count=p.comments.count(),created_at=c.created_at.strftime('%H:%M'))
@login_required
def add_reel_comment(request,reel_id):
    if request.method!='POST': return JsonResponse({'ok':False},status=405)
    r=get_object_or_404(Reel,id=reel_id); content=(request.POST.get('content') or '').strip()[:1000]
    if not content:return JsonResponse({'ok':False,'error':'Comment cannot be empty.'},status=400)
    c=ReelComment.objects.create(user=request.user,reel=r,content=content); _notify(r.author,request.user,'comment',f'@{request.user.username} commented on your reel.')
    return ok(id=c.id,username=request.user.username,content=c.content,count=r.comments.count(),created_at=c.created_at.strftime('%H:%M'))

@login_required
def comments_api(request,kind,object_id):
    if kind=='post': obj=get_object_or_404(Post,id=object_id); items=obj.comments.select_related('user').order_by('-created_at')[:50]
    elif kind=='reel': obj=get_object_or_404(Reel,id=object_id); items=obj.comments.select_related('user').order_by('-created_at')[:50]
    else:return JsonResponse({'ok':False},status=400)
    return JsonResponse({'ok':True,'comments':[{'username':x.user.username,'content':x.content,'time':x.created_at.strftime('%H:%M')} for x in items]})

@login_required
def search(request):
    q=(request.GET.get('q') or '').strip()[:80]; users=User.objects.filter(username__icontains=q)[:20] if q else User.objects.none(); posts=Post.objects.filter(Q(content__icontains=q)|Q(hashtags__name__icontains=q)).distinct()[:20] if q else Post.objects.none(); reels_qs=Reel.objects.filter(Q(caption__icontains=q)|Q(hashtags__name__icontains=q)).distinct()[:20] if q else Reel.objects.none(); tags=Hashtag.objects.filter(name__icontains=q)[:20] if q else Hashtag.objects.none()
    if wants_json(request): return JsonResponse({'ok':True,'users':[u.username for u in users],'posts':[{'id':p.id,'text':p.content[:80]} for p in posts],'reels':[{'id':r.id,'text':r.caption[:80]} for r in reels_qs],'hashtags':[t.name for t in tags]})
    return render(request,'posts/search.html',{'query':q,'users':users,'posts':posts,'reels':reels_qs,'hashtags':tags})

@login_required
def record_view(request,kind,object_id):
    if request.method!='POST': return JsonResponse({'ok':False,'error':'POST required'},status=405)
    if not request.session.session_key: request.session.save()
    if kind=='post': obj=get_object_or_404(Post,id=object_id); kwargs={'post':obj}
    elif kind=='reel': obj=get_object_or_404(Reel,id=object_id); kwargs={'reel':obj}
    else:return JsonResponse({'ok':False},status=400)
    account_views=ContentView.objects.filter(user=request.user,**kwargs).count()
    if account_views>=2:
        count=ContentView.objects.filter(**kwargs).count()
        return ok(count=count,recorded=False,account_limit_reached=True)
    ContentView.objects.create(user=request.user,session_key=request.session.session_key,**kwargs)
    count=ContentView.objects.filter(**kwargs).count(); return ok(count=count,recorded=True)

@login_required
def analytics(request):
    posts=Post.objects.filter(author=request.user); reels_qs=Reel.objects.filter(author=request.user)
    context={'post_count':posts.count(),'reel_count':reels_qs.count(),'post_likes':Like.objects.filter(post__author=request.user).count(),'reel_likes':ReelLike.objects.filter(reel__author=request.user).count(),'post_views':ContentView.objects.filter(post__author=request.user).count(),'reel_views':ContentView.objects.filter(reel__author=request.user).count(),'comment_count':Comment.objects.filter(post__author=request.user).count()+ReelComment.objects.filter(reel__author=request.user).count()}
    context['stats']=[('Posts',context['post_count']),('Reels',context['reel_count']),('Post views',context['post_views']),('Reel views',context['reel_views']),('Post likes',context['post_likes']),('Reel likes',context['reel_likes']),('Comments',context['comment_count'])]
    return render(request,'posts/analytics.html',context)

@login_required
def content_analytics(request,kind,object_id):
    if kind=='post': obj=get_object_or_404(Post,id=object_id); allowed=obj.author==request.user; likes=obj.likes.count(); comments=obj.comments.count(); views=obj.content_views.count(); shares=obj.shares.count(); saves=obj.saves.count()
    elif kind=='reel': obj=get_object_or_404(Reel,id=object_id); allowed=obj.author==request.user; likes=obj.likes.count(); comments=obj.comments.count(); views=obj.content_views.count(); shares=obj.shares.count(); saves=obj.saves.count()
    else:return JsonResponse({'ok':False},status=400)
    if not allowed: return JsonResponse({'ok':False,'error':'Only the creator can view this analysis.'},status=403)
    return ok(kind=kind,id=object_id,views=views,likes=likes,comments=comments,shares=shares,saves=saves)

@login_required
def delete_post(request,post_id):
    p=get_object_or_404(Post,id=post_id)
    if p.author!=request.user:return JsonResponse({'ok':False,'error':'Not allowed'},status=403)
    if request.method=='POST':p.delete();return ok(deleted=True)
    return redirect('home')
@login_required
def delete_reel(request,reel_id):
    r=get_object_or_404(Reel,id=reel_id)
    if r.author!=request.user:return JsonResponse({'ok':False,'error':'Not allowed'},status=403)
    if request.method=='POST':r.delete();return ok(deleted=True)
    return redirect('reels')
