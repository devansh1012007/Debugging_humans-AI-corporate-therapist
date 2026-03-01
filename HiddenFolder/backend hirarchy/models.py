from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class StructureLevel(models.Model):
    """ Defines the 'Rank'. e.g., Level 1: Executive, Level 2: Management """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=50) 
    level_rank = models.IntegerField(help_text="1 is highest (CEO)")

    class Meta:
        ordering = ['level_rank']
        unique_together = ('company', 'level_rank')

class OrgNode(models.Model):
    """
    The 'Position' or 'Seat'.
    - 'name' is the Title (CEO, CTO).
    - 'user' is the person currently sitting in that seat.
    """
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='org_node') #example: elon musk, jeff bezos
    name = models.CharField(max_length=255)# example: CTO, CEO,ETC
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='nodes')
    structure_level = models.ForeignKey(StructureLevel, on_delete=models.PROTECT)# e.g., Executive(ceo, cto), Manager(sales team manage, dev team manager), with relation to numbers on tree . also u cant change level bcoz of on_delete=models.PROTECT 
    
    # SAFETY NET: on_delete=SET_NULL
    # If a boss is deleted, children don't die. They just lose their boss temporarily.
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children'#orgnode_set is default name for reverse lookup, children is more intuitive and makes sense and make it easy to understand
    )

    def __str__(self):
        return f"{self.name} ({self.structure_level.name})"

# --- METRICS (These DO delete if the Node is deleted) ---

class PerformanceMetric(models.Model):
    # If Node deleted -> History Deleted (CASCADE)
    node = models.ForeignKey(OrgNode, on_delete=models.CASCADE, related_name='perf_metrics')
    tasks_completed = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date_recorded = models.DateField(auto_now_add=True)

class MentalHealthMetric(models.Model):
    # If Node deleted -> History Deleted (CASCADE)
    node = models.ForeignKey(OrgNode, on_delete=models.CASCADE, related_name='health_metrics')
    wellness_index = models.IntegerField()
    stress_level = models.IntegerField(default=5)
    date_recorded = models.DateField(auto_now_add=True)

class ReportSnapshot(models.Model): #in the main code v need many of these and this need to be edited 
    REPORT_TYPES = [('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly')]#this list is a Choices definition. It is used to create a "dropdown" effect in the database, ensuring that only specific, valid strings can be saved into a field.
    node = models.ForeignKey(OrgNode, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()