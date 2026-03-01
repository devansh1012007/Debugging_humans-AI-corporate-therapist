from django.db import models
from django.contrib.auth.models import User

# --- STRUCTURE ---
class StructureLevel(models.Model):
    """ Defines the 'Rank'. e.g., Level 1: Executive, Level 2: Management """
    company = models.ForeignKey(on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=50) 
    level_rank = models.IntegerField(help_text="1 is highest (CEO)")

    class Meta:
        ordering = ['level_rank']
        #unique_together = ('level_rank')

class OrgNode(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='org_node')
    name = models.CharField(max_length=255) # Position Title (e.g., "VP Sales")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    level = models.ForeignKey(StructureLevel, on_delete=models.PROTECT, null=True)
    def __str__(self): return self.name

# --- RAW INPUT (Daily Logs) ---
class MentalHealthMetric(models.Model):
    node = models.ForeignKey(OrgNode, on_delete=models.CASCADE, related_name='health_metrics')
    wellness_index = models.IntegerField() # 1-10
    stress_level = models.IntegerField()   # 1-10
    date_recorded = models.DateField(auto_now_add=True)

# --- PROCESSED OUTPUT (Midnight Snapshots) ---
class ReportSnapshot(models.Model):
    node = models.ForeignKey(OrgNode, on_delete=models.CASCADE, related_name='snapshots')
    date_created = models.DateField(auto_now_add=True)
    
    # This stores the "AI Processed" team average
    data = models.JSONField() 
    
    class Meta:
        get_latest_by = 'date_created'

class personalData(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_data')
    content = models.JSONField()