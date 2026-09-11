from django.urls import path
from .views import profile_view, edit_profile, friends, toggle_follow

urlpatterns = [
    path('edit/', edit_profile, name='edit_profile'),
    path('friends/', friends, name='friends'),
    path('<str:username>/', profile_view, name='profile'),
    path('<str:username>/follow/', toggle_follow, name='toggle_follow'),
]
