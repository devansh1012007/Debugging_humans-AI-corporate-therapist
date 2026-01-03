# project/urls.py
from django.contrib import admin
from django.urls import path, include
#from app_1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_1.urls')),
    #path('accounts/', include('allauth.urls')),
]
