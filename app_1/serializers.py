#serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.fields import CurrentUserDefault
from .models import (
    Tharipistneeded, UserDrillDown, UserFeedback, UserHomepageDB, UserChatDB, UserPersonalityData, 
    TeamData, UserPsycoData, UserPsycoProcessedData, UserPsycoProcessedDataHistory,
    Company, UserDashboard, UserDashboardHistory, TeamDataHistory, 
    UserChatSummary, StructureLevel, OrgNode,UserConsent,UserPsycoDataHistory
)


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

class UserPsycoProcessedDataSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserPsycoProcessedData
        fields = ['content', 'owner']

class UserPsycoProcessedDataHistorySerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserPsycoProcessedDataHistory
        fields = ['content', 'owner']

class UserPsycoDataHistorySerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserPsycoDataHistory
        fields = ['content', 'owner']

class UserPersonalityDataSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserPersonalityData
        fields = ['content', 'owner']
        
class UserPersonalityDataHistoricSerializer(serializers.ModelSerializer):
        owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
        fields = ['content', 'owner']

class UserDashboardSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())# 
    class Meta:
        model = UserDashboard
        fields = ['owner', 'content']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', 'created_at']

class StructureLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StructureLevel
        fields = ['company', 'name', 'level_rank']

class OrgNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgNode
        fields = ['id', 'user', 'name', 'company', 'structure_level', 'parent']

class TeamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamData
        fields = ['node', 'content']

class UserFeedbackSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserFeedback
        fields = ['feedback', 'rating', 'submitted_at', 'owner']
    def create(self, validated_data):
        return UserFeedback.objects.create(**validated_data)

class UserConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConsent
        fields = ['user', 'ip_address', 'user_agent', 'agreed_at', 'consent_version']
        read_only_fields = ['id', 'ip_address', 'user_agent', 'agreed_at', 'user']



class UserDashboardHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDashboardHistory
        fields = ['owner', 'timestamp', 'content']

class TeamDataHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamDataHistory
        fields = ['node', 'timestamp', 'content']

class UserChatSummarySerializer(serializers.ModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserChatSummary
        fields = ['owner', 'content', 'chat']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            #last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class TherapistNeededSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tharipistneeded
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True}, 
            'submitted_at': {'read_only': True},
            'in_need': {'read_only': True}
        }