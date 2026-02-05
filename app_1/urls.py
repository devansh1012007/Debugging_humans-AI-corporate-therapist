# app1/urls.py
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import UserConsentViewSet, OldChatsViewSet,ChatViewSet, OrgNodeViewSet, PrivacyPolicyAcceptanceViewSet, RegisterView, UserDrillDownViewSet, UserFeedbackViewSet, ConsentFormAcceptanceViewSet, PrivacyPolicyAcceptanceViewSet, User#UserPsycoDataViewSet

router = DefaultRouter()# creating a router instance to register viewsets 
# router basicly handels all the reqests and it 
router.register(r'Chats', OldChatsViewSet, basename='Chats') # this has only previous chats history
router.register(r'ChatData', ChatViewSet, basename='ChatData')# this has all the previous chats beteween user and ai
#router.register(r'UserPsycoDataViewSet', UserPsycoDataViewSet, basename='UserPsycoData')
router.register(r'DashBoardData', OrgNodeViewSet, basename='DashBoardData')# for both team and individual dashboards
router.register(r'UserFeedback', UserFeedbackViewSet, basename='UserFeedback')
router.register(r'PrivacyPolicyAcceptance', PrivacyPolicyAcceptanceViewSet, basename='PrivacyPolicyAcceptance')
router.register(r'UserConsent', UserConsentViewSet, basename='UserConsent')
#router.register(r'UserPsycoData', UserPsycoDataViewSet, basename='UserPsycoData')
router.register(r'UserDrillDown', UserDrillDownViewSet, basename='UserDrillDown')
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),# JWT login endpoint built-in view # not needed as v r using allauth for authentication, best for barebones setup
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='auth_register'),# not needed as v r using allauth for authentication, best for barebones setup
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    '''path('PrivacyPolicy/', PrivacyPolicy, name='PrivacyPolicy'),
    path('TermsOfService/', TermsOfService, name='TermsOfService'),
    path('UserPsycoData/', UserPsycoData, name='UserPsycoData'),
    path('teamdata2/', TeamData2, name='TeamData2'),
    '''
]

'''
this is urls.py of my backend, i want u to make changes in api urls accordingly'''