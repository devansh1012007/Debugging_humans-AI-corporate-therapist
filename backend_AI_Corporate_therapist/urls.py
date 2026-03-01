# project/urls.py
from django.contrib import admin
from django.urls import path, include  # Added 'include'
#from django.views.generic.base import RedirectView
from app_1.views import RegisterView, GoogleLogin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', include('app_1.urls')),

    path('admin/', admin.site.urls),
    
    path('accounts/', include('allauth.urls')), 

    #path('api/register/', RegisterView.as_view()),
    #path('api/login/', TokenObtainPairView.as_view()),
    #path('api/token/refresh/', TokenRefreshView.as_view()),
    #path('api/profile/', ProfileView.as_view()),
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
]