from django.urls import path
from .views import login_view,register_view,logout_view,verify_2fa
urlpatterns=[path('login/',login_view,name='login'),path('verify-2fa/',verify_2fa,name='verify_2fa'),path('register/',register_view,name='register'),path('logout/',logout_view,name='logout')]
