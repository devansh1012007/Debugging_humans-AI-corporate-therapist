# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    GoogleLogin, OldChatsViewSet, ChatViewSet, OrgNodeViewSet, ProfileView, 
    UserFeedbackViewSet, PrivacyPolicyAcceptanceViewSet, 
    UserConsentViewSet, UserDrillDownViewSet, RegisterView
)

router = DefaultRouter()
router.register(r'Chats', OldChatsViewSet, basename='Chats')
router.register(r'ChatData', ChatViewSet, basename='ChatData')
router.register(r'DashBoardData', OrgNodeViewSet, basename='DashBoardData')
router.register(r'UserFeedback', UserFeedbackViewSet, basename='UserFeedback')
router.register(r'PrivacyPolicyAcceptance', PrivacyPolicyAcceptanceViewSet, basename='PrivacyPolicyAcceptance')
router.register(r'UserConsent', UserConsentViewSet, basename='UserConsent')
router.register(r'UserDrillDown', UserDrillDownViewSet, basename='UserDrillDown')


'''urlpatterns = [
    # Auth Endpoints
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    
]'''

urlpatterns = [
    path('', include(router.urls)),
        path('accounts/', include('allauth.urls')), 

    path('api/register/', RegisterView.as_view()),
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/profile/', ProfileView.as_view()),
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
]