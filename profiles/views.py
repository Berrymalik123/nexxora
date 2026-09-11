from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .forms import ProfileForm, UserProfileForm
from .models import Profile
from posts.models import Post, Reel, Like, ReelLike
from social.models import ContentView
from django.db.models import Q
from notifications.models import Notification
User=get_user_model()
def ensure_profile(user): return Profile.objects.get_or_create(user=user)[0]
def profile_view(request,username):
    u=get_object_or_404(User,username=username); p=ensure_profile(u); posts=Post.objects.filter(author=u).order_by('-created_at'); reels=Reel.objects.filter(author=u).order_by('-created_at'); following=request.user.is_authenticated and p.followers.filter(pk=request.user.pk).exists()
    stats={'posts':posts.count(),'reels':reels.count(),'views':ContentView.objects.filter(Q(post__author=u)|Q(reel__author=u)).count() if False else ContentView.objects.filter(post__author=u).count()+ContentView.objects.filter(reel__author=u).count(),'likes':Like.objects.filter(post__author=u).count()+ReelLike.objects.filter(reel__author=u).count()}
    return render(request,'profiles/profile.html',{'profile_user':u,'profile':p,'posts':posts,'reels':reels,'is_following':following,'stats':stats})
@login_required
def edit_profile(request):
    p=ensure_profile(request.user); uf=UserProfileForm(request.POST or None,instance=request.user); pf=ProfileForm(request.POST or None,request.FILES or None,instance=p)
    if request.method=='POST' and uf.is_valid() and pf.is_valid(): uf.save(); pf.save(); messages.success(request,'Profile updated.'); return redirect('profile',username=request.user.username)
    return render(request,'profiles/edit_profile.html',{'user_form':uf,'profile_form':pf})
@login_required
def friends(request):
    query=(request.GET.get('q') or '').strip()[:80]
    users=User.objects.exclude(pk=request.user.pk)
    if query:
        users=users.filter(Q(username__icontains=query)|Q(first_name__icontains=query)|Q(last_name__icontains=query)|Q(email__icontains=query))
    users=list(users.select_related('profile').order_by('username')[:100])
    following_ids=set(Profile.objects.filter(user__in=users,followers=request.user).values_list('user_id',flat=True))
    return render(request,'profiles/friends.html',{'people':users,'query':query,'following_ids':following_ids})
@login_required
def toggle_follow(request,username):
    target=get_object_or_404(User,username=username)
    if target==request.user: return JsonResponse({'ok':False,'error':'You cannot follow yourself.'},status=400)
    p=ensure_profile(target); following=p.followers.filter(pk=request.user.pk).exists()
    if following: p.followers.remove(request.user)
    else: p.followers.add(request.user); Notification.objects.create(recipient=target,actor=request.user,notification_type='follow',text=f'@{request.user.username} started following you.')
    return JsonResponse({'ok':True,'following':not following,'count':p.follower_count})
