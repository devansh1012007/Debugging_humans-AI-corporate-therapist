
from django.db import models
from django.contrib.auth.models import User
import uuid

class OwnedModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        abstract = True

class UserHomepageDB(OwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Chat")
    AiMode = models.CharField(max_length=20, default="therapy")
    last_updated = models.DateTimeField(auto_now=True)

class UserChatDB(OwnedModel):
    chat = models.OneToOneField(UserHomepageDB, on_delete=models.CASCADE, related_name="history")
    content = models.JSONField(default=list)
    to_be_summarized = models.BooleanField(default=False)

class UserChatSummary(OwnedModel):
    content = models.JSONField()
    chat = models.OneToOneField(UserHomepageDB, on_delete=models.CASCADE, related_name="summary")

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
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='org_node')
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='nodes')
    structure_level = models.ForeignKey(StructureLevel, on_delete=models.PROTECT)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def __str__(self):
        return f"{self.name} ({self.structure_level.name})"

class UserDashboard(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.JSONField()


class UserDashboardHistory(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.JSONField()

class UserDrillDown(OwnedModel):
    content = models.JSONField(default=list)

class TeamData(models.Model):
    node = models.OneToOneField(OrgNode, on_delete=models.CASCADE, related_name='team_data')
    content = models.JSONField(default=list)

class TeamDataHistory(models.Model):
    node = models.OneToOneField(OrgNode, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.JSONField(default=list)


class UserPsycoData(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    content = models.JSONField(default=list)

class UserPsycoDataHistory(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    content = models.JSONField(default=list)

class UserPersonalityData(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    content = models.JSONField(default=list)

class UserPersonalityDataHistoric(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    content = models.JSONField(default=list)
    
class UserFeedback(OwnedModel):
    feedback = models.TextField()
    rating = models.IntegerField(default=5)
    submitted_at = models.DateTimeField(auto_now_add=True)

class UserConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    consent_version = models.CharField(max_length=50, default="v1.0-2026")  # e.g., "v1.0-2023"
    agreed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True) # Stores browser info

    def __str__(self):
        return f"Consent {self.consent_version} by {self.ip_address}"
    

class Tharipistneeded(OwnedModel):
    in_need = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)