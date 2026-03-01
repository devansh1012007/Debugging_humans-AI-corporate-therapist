import json
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import (
    Company, StructureLevel, OrgNode, 
    TeamData, TeamDataHistory,
    UserDashboard, UserDashboardHistory,
    UserChatDB, UserHomepageDB
)
from ..tasks import process_midnight_snapshots,get_report

class MidnightSnapshotTest(TestCase):
    
    def setUp(self):
        """Create test data"""
        self.company = Company.objects.create(name="Test Corp")
        self.ceo_level = StructureLevel.objects.create(
            company=self.company,
            name="CEO",
            level_rank=1
        )
        self.manager_level = StructureLevel.objects.create(
            company=self.company,
            name="Manager",
            level_rank=2
        )
        
        self.ceo_user = User.objects.create_user(
            username='ceo',
            password='test123'
        )
        self.manager_user = User.objects.create_user(
            username='manager',
            password='test123'
        )
        
        self.ceo_node = OrgNode.objects.create(
            user=self.ceo_user,
            name="CEO Node",
            company=self.company,
            structure_level=self.ceo_level,
            parent=None
        )
        
        self.manager_node = OrgNode.objects.create(
            user=self.manager_user,
            name="Manager Node",
            company=self.company,
            structure_level=self.manager_level,
            parent=self.ceo_node
        )
        
        chat = UserHomepageDB.objects.create(
            owner=self.manager_user,
            title="Test Chat"
        )
        UserChatDB.objects.create(
            owner=self.manager_user,
            chat=chat,
            content=[
                {"role": "user", "message": "I'm feeling stressed"},
                {"role": "assistant", "message": "Let's talk about that"}
            ]
        )
    
    def test_team_data_format(self):
        """Test TeamData JSON format"""
        process_midnight_snapshots()
        
        team_data = TeamData.objects.get(node=self.ceo_node)
        
        print("\n=== TEAM DATA ===")
        print(json.dumps(team_data.content, indent=2))
        
        # Validate structure
        self.assertIsInstance(team_data.content, list)
        self.assertEqual(len(team_data.content), 1)
        
        entry = team_data.content[0]
        self.assertIn('content', entry)
        
        content = entry['content']
        self.assertIn('policy_changes', content)
        self.assertIn('common_problems', content)
        self.assertIn('recommendations', content)
        
        self.assertIsInstance(content['policy_changes'], list)
        if content['policy_changes']:
            policy = content['policy_changes'][0]
            self.assertIn('title', policy)
            self.assertIn('description', policy)
    
    def test_user_dashboard_format(self):
        """Test UserDashboard JSON format"""
        process_midnight_snapshots()
        
        dashboard = UserDashboard.objects.get(owner=self.manager_user)
        
        print("\n=== USER DASHBOARD ===")
        print(json.dumps(dashboard.content, indent=2))
        
        self.assertIsInstance(dashboard.content, list)
        self.assertEqual(len(dashboard.content), 1)
        
        entry = dashboard.content[0]
        self.assertIn('content', entry)
        
        content = entry['content']
        self.assertIn('positives', content)
        self.assertIn('common_problems', content)
        self.assertIn('recommendations', content)
        
        self.assertIsInstance(content['positives'], list)
        if content['positives']:
            positive = content['positives'][0]
            self.assertIn('positive', positive)
    
    def test_history_tracking(self):
        """Test that history is properly tracked"""
        process_midnight_snapshots()
        
        team_history = TeamDataHistory.objects.get(node=self.ceo_node)
        self.assertIsInstance(team_history.content, list)
        self.assertGreater(len(team_history.content), 0)
        
        user_history = UserDashboardHistory.objects.get(owner=self.manager_user)
        self.assertIsInstance(user_history.content, list)
        self.assertGreater(len(user_history.content), 0)
        #cp /test_midnight_snapshots.py /Documents/temp code storage/Debugging_humans-AI-corporate-therapist/app_1/tests/