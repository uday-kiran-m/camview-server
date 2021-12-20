from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='homeweb'),
    path('video/',views.vidstream,name='video'),
]
