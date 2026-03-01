from django.contrib import admin
from .models import (
    Company, StructureLevel, OrgNode, 
    UserHomepageDB, UserChatDB, 
    UserDashboard, UserDrillDown, 
    UserFeedback, UserConsent
)

# 1. Company & Structure
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(StructureLevel)
class StructureLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_rank', 'company')
    ordering = ['level_rank']

@admin.register(OrgNode)
class OrgNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_name', 'structure_level', 'parent')
    list_filter = ('company', 'structure_level')
    
    def user_name(self, obj):
        return obj.user.username if obj.user else "VACANT"

# 2. User Data (Chat & Dashboards)
@admin.register(UserHomepageDB)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'last_updated')

@admin.register(UserChatDB)
class ChatContentAdmin(admin.ModelAdmin):
    list_display = ('owner', 'chat')

@admin.register(UserDashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('owner',)

@admin.register(UserDrillDown)
class DrillDownAdmin(admin.ModelAdmin):
    list_display = ('owner',)

# 3. Compliance
admin.site.register(UserFeedback)
admin.site.register(UserConsent)
