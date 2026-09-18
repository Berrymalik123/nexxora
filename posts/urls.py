from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('reels/', views.reels, name='reels'),
    path('create/', views.create_post, name='create_post'),
    path('reels/create/', views.create_reel, name='create_reel'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/<str:kind>/<int:object_id>/', views.content_analytics, name='content_analytics'),
    path('view/<str:kind>/<int:object_id>/', views.record_view, name='record_view'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('reels/like/<int:reel_id>/', views.like_reel, name='like_reel'),
    path('save/<int:post_id>/', views.save_post, name='save_post'),
    path('reels/save/<int:reel_id>/', views.save_reel, name='save_reel'),
    path('share/<int:post_id>/', views.share_post, name='share_post'),
    path('reels/share/<int:reel_id>/', views.share_reel, name='share_reel'),
    path('reels/remix/<int:reel_id>/', views.remix_reel, name='remix_reel'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('reels/delete/<int:reel_id>/', views.delete_reel, name='delete_reel'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('reels/comment/<int:reel_id>/', views.add_reel_comment, name='add_reel_comment'),
    path('comments/<str:kind>/<int:object_id>/', views.comments_api, name='comments_api'),
]
