# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    OldChatsViewSet, ChatViewSet, OrgNodeViewSet, TherapistNeededView, UserDashboardViewSet, 
    UserFeedbackViewSet,  UserPsycoProcessedDataViewSet,UserPsycoProcessedDataHistoryViewSet,
    UserConsentViewSet, UserDrillDownViewSet, RegisterView
)

router = DefaultRouter()
router.register(r'Chats', OldChatsViewSet, basename='Chats')
router.register(r'ChatData', ChatViewSet, basename='ChatData')
router.register(r'DashBoardData', OrgNodeViewSet, basename='DashBoardData')
router.register(r'UserFeedback', UserFeedbackViewSet, basename='UserFeedback')
#router.register(r'PrivacyPolicyAcceptance', PrivacyPolicyAcceptanceViewSet, basename='PrivacyPolicyAcceptance')
router.register(r'UserConsent', UserConsentViewSet, basename='UserConsent')
router.register(r'UserDrillDown', UserDrillDownViewSet, basename='UserDrillDown')
router.register(r'UserDashboard', UserDashboardViewSet, basename='UserDashboard')
router.register(r'TherapistNeeded', TherapistNeededView, basename='TherapistNeeded')
router.register(r'UserPsycoProcessedData', UserPsycoProcessedDataViewSet, basename='UserPsycoProcessedData')
router.register(r'UserPsycoProcessedDataHistory', UserPsycoProcessedDataHistoryViewSet, basename='UserPsycoProcessedDataHistory')
#router.register(r'Download', Download, basename='TherapistNeeded')
urlpatterns = [
    path('', include(router.urls)),
    #path('accounts/', include('allauth.urls')), 
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    #path('google/', GoogleLogin.as_view(), name='google_login'),
]
