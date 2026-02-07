#serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.fields import CurrentUserDefault
from .models import (
    UserDrillDown, UserFeedback, UserHomepageDB, UserChatDB, UserPersonalityData, 
    TeamData, PrivacyPolicyAcceptance, UserPsycoData, 
    Company, UserDashboard, UserDashboardHistory, TeamDataHistory, 
    UserChatSummary, StructureLevel, OrgNode,UserConsent
)

# --- USER SERIALIZERS ---

class HomePageSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault()) 
    class Meta:
        model = UserHomepageDB
        fields = ['id', 'title', 'last_updated', 'AiMode', 'owner']

class ChatSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserChatDB
        fields = ['id', 'chat', 'content', 'owner']

class UserDrillDownSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserDrillDown
        fields = ['content', 'owner']

class UserPsycoDataSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserPsycoData
        fields = ['content', 'owner']
    
class UserPersonalityDataSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserPersonalityData
        fields = ['content', 'owner']

class UserDashboardSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())# 
    class Meta:
        model = UserDashboard
        fields = ['owner', 'content']

# --- ORG SERIALIZERS ---

# RENAMED to avoid conflict with Model 'Company'
class CompanySerializer(serializers.ModelSerializer):
    # REMOVED 'owner' because Company model does not have an owner field
    class Meta:
        model = Company
        fields = ['name', 'created_at']

class StructureLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StructureLevel
        fields = ['company', 'name', 'level_rank']

class OrgNodeSerializer(serializers.ModelSerializer):
    # Removed 'owner' from fields as we removed it from Model
    class Meta:
        model = OrgNode
        fields = ['id', 'user', 'name', 'company', 'structure_level', 'parent']

class TeamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamData
        fields = ['node', 'content']

# --- FORM & FEEDBACK SERIALIZERS ---

class UserFeedbackSerializer(serializers.ModelSerializer):
    # ADDED owner hidden field (Required by OwnedModel)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserFeedback
        fields = ['feedback', 'rating', 'submitted_at', 'owner']
    def create(self, validated_data):
        return UserFeedback.objects.create(**validated_data)
class PrivacyPolicyAcceptanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicyAcceptance
        fields = ['user', 'ip_address', 'user_agent', 'accepted_at', 'current_version']
        #read_only_fields = ['id', 'accepted_at', 'created_at', 'user']

class UserConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConsent
        # We only require 'consent_version' from the user input
        fields = ['user', 'ip_address', 'user_agent', 'accepted_at', 'current_version']
        #read_only_fields = ['id', 'ip_address', 'user_agent', 'agreed_at', 'user']

# --- HISTORY & SUMMARY SERIALIZERS ---

class UserDashboardHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDashboardHistory
        fields = ['owner', 'timestamp', 'content']

class TeamDataHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamDataHistory
        fields = ['node', 'timestamp', 'content']

class UserChatSummarySerializer(serializers.ModelSerializer):
    # ADDED owner hidden field
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserChatSummary
        fields = ['owner', 'content', 'chat']

# --- AUTH SERIALIZER ---

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
