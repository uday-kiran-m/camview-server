from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('devices/',views.devices,name='devices'),
    path('login/',views.loginuser,name='login'),
    path('logout',views.logoutuser,name='logout')
]
