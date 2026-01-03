# app1/urls.py
from django.urls import path, include
from .views import GoogleLogin
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter
from .views import OldChatsViewSet,ChatViewSet, RegisterView,problemsViewSet,TeamMembersViewSet,TeamDataViewSet

router = DefaultRouter()# creating a router instance to register viewsets
router.register(r'Chats', OldChatsViewSet, basename='Chats') # registering the ItemViewSet to handle /items/ endpoints -> does the main tasks
router.register(r'ChatData', ChatViewSet, basename='ChatData')
router.register(r'Problems', problemsViewSet, basename='Problems')
router.register(r'TeamMembers', TeamMembersViewSet, basename='TeamMembers')
router.register(r'TeamData', TeamDataViewSet, basename='TeamData')
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),# JWT login endpoint built-in view # not needed as v r using allauth for authentication, best for barebones setup
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),# not needed as v r using allauth for authentication, best for barebones setup
    path('dj-rest-auth/', include('dj_rest_auth.urls')), # Standard login/logout endpoints
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')), # Registration
    path('auth/google/', GoogleLogin.as_view(), name='google_login')
]

