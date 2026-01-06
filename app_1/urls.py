# app1/urls.py
from django.urls import path, include
# Import views used to generate Login tokens
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Import the Router to automatically generate URL paths for standard views
from rest_framework.routers import DefaultRouter
from .views import OldChatsViewSet, ChatViewSet, RegisterView, problemsViewSet, TeamMembersViewSet, TeamDataViewSet

# Create a router
router = DefaultRouter()
# Register the views with the router
# e.g., this makes URLs like /Chats/ and /Chats/<id>/ work automatically
router.register(r'Chats', OldChatsViewSet, basename='Chats') 
router.register(r'ChatData', ChatViewSet, basename='ChatData')
router.register(r'Problems', problemsViewSet, basename='Problems')
router.register(r'TeamMembers', TeamMembersViewSet, basename='TeamMembers')
router.register(r'TeamData', TeamDataViewSet, basename='TeamData')

urlpatterns = [
    # Login endpoint: Sending username/password here returns an access token
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Include all the router URLs defined above
    path('', include(router.urls)),
    # Register endpoint: For creating new accounts
    path('register/', RegisterView.as_view(), name='auth_register'),
    # Refresh endpoint: To get a new access token when the old one expires
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]