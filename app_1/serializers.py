# serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.fields import CurrentUserDefault
from .models import UserHomepageDB, UserChatDB, UserProblems, TeamMembers, TeamData

# Translator for the Chat List (Homepage)
class HomePageSerializer(serializers.ModelSerializer):
    # Automatically set the 'owner' to the currently logged-in user (hidden from the user)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault()) 
    class Meta:
        model = UserHomepageDB
        # List the fields to include in the JSON output
        fields = ['id', 'title', 'last_updated','AiMode', 'owner']

# Translator for the specific Chat History
class ChatSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserChatDB
        fields = ['id','chat', 'content', 'owner']

# Translator for User Problems
class UserProblemSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = UserProblems
        fields = ['content', 'owner']

# Translator for Team Members
class TeamMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembers
        fields = ['teamname', 'content']

# Translator for Team Dashboard Data
class TeamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamData
        fields = ['summary', 'recommendation', 'common_problems']

# Translator for Registration (Sign Up)
class RegisterSerializer(serializers.ModelSerializer):
    # Ensure the email provided is unique in the database
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User 
        fields = ('username', 'password', 'email')
        # Ensure the password is can be written (sent to server) but never read (sent back to user)
        extra_kwargs = {'password': {'write_only': True}}

    # Logic to create the user when data is received
    def create(self, validated_data):
        # Create the user securely (hashing the password)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user