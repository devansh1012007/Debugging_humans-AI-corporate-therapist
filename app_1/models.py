# models.py
# Import standard database tools
from django.db import models
# Import the built-in User system (handles usernames/passwords)
from django.contrib.auth.models import User
# Import a tool to generate unique random IDs
import uuid

# Base Model: A template for other models
class OwnedModel(models.Model):
    # Every model inheriting this will have an "owner" (a link to a User)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True # Tells Django not to build a table for this, just use it as a template

# Model 1: User Homepage (The "Cover" of the chat)
class UserHomepageDB (OwnedModel):
    # The title of the chat (e.g., "Work Stress")
    title = models.CharField(max_length=255, default="New Chat") 
    # A unique ID for the chat (better than numbers like 1, 2, 3)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The setting for the AI (e.g., therapy mode)
    AiMode = models.CharField(max_length=20,default="therapy")
    # Timestamp for when the chat was last touched
    last_updated = models.DateTimeField(auto_now=True)
    class Meta:
        # Sort results so the newest chats appear first
        ordering = ['-last_updated']
    # A string representation (helper for the admin panel)
    def __str__(self):
        return f"{self.owner.username} - {self.title}"

# Model 2: User Chat (The "Pages" of the chat)
class UserChatDB(OwnedModel):
    # Links strictly to one HomepageDB entry (One-to-One relationship)
    chat = models.OneToOneField(UserHomepageDB, on_delete=models.CASCADE, related_name="history") 
    # Stores the actual messages as a list of data (JSON)
    content = models.JSONField(default=list)

# Model 3: User Problems (Assessment results)
class UserProblems(OwnedModel):
    # Text field to describe the user's problems
    content = models.TextField()

# Model 4: Team Members (Who is in which team)
class TeamMembers(models.Model): 
    # Name of the team
    teamname = models.CharField(max_length=255, default="team")
    # A list of users in that team (JSON format)
    content = models.JSONField(default=list) 

# Model 5: Team Data (The Dashboard Reports)
# Inherits from TeamMembers, so it is linked to a specific team
class TeamData(TeamMembers):
    # Text summary of the team's status
    summary = models.TextField()
    # Advice for the manager
    recommendation = models.TextField()
    # List of common issues in the team
    common_problems = models.JSONField(default=list)

# Model 6: Website Usage Data (Currently disabled)
# This code is commented out and not active.
'''
class WebsiteData(models.Model):
    user = models.JSONField()
'''