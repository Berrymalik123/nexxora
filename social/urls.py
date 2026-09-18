from django.urls import path
from .views import report_content,inbox,conversation,share_reel_message,open_one_time_message,call_signal
urlpatterns=[path('report/<str:kind>/<int:object_id>/',report_content,name='report_content'),path('messages/',inbox,name='inbox'),path('messages/share-reel/<int:reel_id>/',share_reel_message,name='share_reel_message'),path('messages/one-time/<int:message_id>/open/',open_one_time_message,name='open_one_time_message'),path('messages/call/<str:username>/',call_signal,name='call_signal'),path('messages/<str:username>/',conversation,name='conversation')]
