# app_1/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings

# --- BASE MODEL ---
class OwnedModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class StructureLevel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=100) 
    level_rank = models.IntegerField(help_text="1 is highest (CEO)")

    class Meta:
        ordering = ['level_rank']

class OrgNode(models.Model):
    # Removed 'owner' - 'user' is sufficient to know who holds the position
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='org_node')
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='nodes')
    structure_level = models.ForeignKey(StructureLevel, on_delete=models.PROTECT)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def __str__(self):
        return f"{self.name} ({self.structure_level.name})"

# --- USER DATA MODELS ---

class UserHomepageDB(OwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Chat")
    AiMode = models.CharField(max_length=20, default="therapy")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_updated']
        
    def __str__(self): return f"{self.owner.username} - {self.title}"

class UserChatDB(OwnedModel):
    chat = models.OneToOneField(UserHomepageDB, on_delete=models.CASCADE, related_name="history")
    content = models.JSONField(default=list)

class UserDashboard(OwnedModel):
    # Removed direct User link to avoid conflicts. Access via Node -> User
    node = models.OneToOneField(OrgNode, on_delete=models.CASCADE, related_name='user_dashboard')
    content = models.JSONField()

# Fixed Typo: Dashbioard -> Dashboard
class UserDashboardHistory(models.Model):
    dashboard = models.ForeignKey(UserDashboard, on_delete=models.CASCADE, related_name='history')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

class UserDrillDown(OwnedModel):
    # owner is inherited
    content = models.JSONField(default=list)

# --- TEAM DATA MODELS ---

class TeamData(models.Model):
    node = models.OneToOneField(OrgNode, on_delete=models.CASCADE, related_name='team_data')
    content = models.JSONField(default=dict)

class TeamDataHistory(models.Model):
    # Changed 'owner' to 'node_ref' to avoid confusion with User model
    node_ref = models.ForeignKey(OrgNode, on_delete=models.CASCADE)
    team_data = models.ForeignKey(TeamData, on_delete=models.CASCADE, related_name='history_entries')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

# --- MISC MODELS ---

class UserPsycoData(OwnedModel):
    content = models.JSONField()

# Fixed Typo: Summery -> Summary
class UserChatSummary(OwnedModel):
    content = models.JSONField()

class UserPersonalityData(OwnedModel):
    content = models.JSONField()

class UserFeedback(OwnedModel):
    feedback = models.TextField()
    rating = models.IntegerField(default=5)
    submitted_at = models.DateTimeField(auto_now_add=True)

class PrivacyPolicyAcceptance(OwnedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    consent_version = models.CharField(max_length=50)  # e.g., "v1.0-2023"
    agreed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True) # Stores browser info

    def __str__(self):
        return f"Consent {self.consent_version} by {self.ip_address}"
    
class UserConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    consent_version = models.CharField(max_length=50)  # e.g., "v1.0-2023"
    agreed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True) # Stores browser info

    def __str__(self):
        return f"Consent {self.consent_version} by {self.ip_address}"