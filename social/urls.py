from django.urls import path
from .views import report_content,inbox,conversation
urlpatterns=[path('report/<str:kind>/<int:object_id>/',report_content,name='report_content'),path('messages/',inbox,name='inbox'),path('messages/<str:username>/',conversation,name='conversation')]
