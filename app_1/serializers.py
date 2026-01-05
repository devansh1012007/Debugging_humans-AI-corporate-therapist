# serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.fields import CurrentUserDefault
from .models import UserHomepageDB, UserChatDB, UserProblems, TeamMembers, TeamData
from rest_framework.validators import UniqueValidator

class HomePageSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault()) 
    class Meta:
        model = UserHomepageDB
        fields = ['id', 'title', 'last_updated','AiMode', 'owner']

class ChatSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserChatDB
        fields = ['id','chat', 'content', 'owner']


    
class UserProblemSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserProblems
        fields = ['content', 'owner']
        #read_only_fields = ['content', 'owner']

class TeamMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembers
        fields = ['teamname', 'content']

class TeamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamData
        fields = ['summary', 'recommendation', 'common_problems']# v need to make it read only for all http request
        #read_only_fields = ['summary', 'recommendation', 'common_problems']

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User #built-in User model
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # .create_user() handles password hashing automatically
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user