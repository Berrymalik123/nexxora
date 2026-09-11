from django.urls import path
from .views import notifications_view,mark_read
urlpatterns=[path('',notifications_view,name='notifications'),path('read/',mark_read,name='mark_notifications_read'),path('read/<int:notification_id>/',mark_read,name='mark_notification_read')]
