from django.test import TestCase
from unittest.mock import patch, MagicMock
from app_1.tasks import get_report
from app_1.models import User, UserPsycoData, UserPsycoDataHistory, UserPersonalityData, UserPersonalityDataHistoric
import json
class GetReportTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(username='testuser_report', email='report@test.com', password='password')

    @patch('app_1.tasks.assesment')
    @patch('app_1.tasks.summarize_chat_history')
    @patch('app_1.tasks.UserChatDB.objects.filter')
    def test_get_report_basic_flow(self, mock_chat_filter, mock_summarize, mock_assessment):
        """
        Test the basic flow of get_report: fetching chats, assessing, and saving results.
        """
        # 1. Mock Chat Data
        # We mock the chat object to ensure 'content' acts as a string (matching get_report logic)
        mock_chat = MagicMock()
        mock_chat.content = [{"message": "I am feeling happy today and ready to work."}]
    
        mock_chat_filter.return_value = [mock_chat]

        # 2. Mock AI Responses
        mock_assessment.return_value = {
            "Personality": {"Openness": "High"},
            "Burnout": {"Score": "Low"}
        }
        mock_summarize.return_value = "Summary of chat history"

        # 3. Run the function
        get_report()

        # 4. Assertions for Psycho Data (First loop in get_report)
        psycho_data = UserPsycoData.objects.get(owner=self.user)
        # Verify data was saved (mock_assessment return value)
        self.assertEqual(psycho_data.content, mock_assessment.return_value)
        
        # Verify History was created
        psycho_history = UserPsycoDataHistory.objects.get(owner=self.user)
        self.assertEqual(len(psycho_history.content), 1)
        self.assertEqual(psycho_history.content[0]['content'], mock_assessment.return_value)
        # Check that date is a string (ISO format) - requires the FIX below
        self.assertIsInstance(psycho_history.content[0]['date'], str)

        # 5. Assertions for Personality Data (Second loop in get_report)
        personality_data = UserPersonalityData.objects.get(owner=self.user)
        #UserPsyco = UserPsycoData.objects.get(owner=self.user)
        #personality_data = UserPersonalityDataHistoric.objects.get(owner=self.user)
        personality_data_History = UserPersonalityDataHistoric.objects.get(owner=self.user)
        # Verify data was saved. Note: Logic in tasks.py wraps it in a list -> [AI_data]
        self.assertEqual(personality_data.content, [mock_assessment.return_value])
        print(json.dumps(personality_data.content ))
        print(json.dumps(psycho_data.content))
        print(json.dumps(psycho_history.content))
        print(json.dumps(personality_data_History.content))
    @patch('app_1.tasks.assesment')
    @patch('app_1.tasks.summarize_chat_history')
    @patch('app_1.tasks.UserChatDB.objects.filter')
    def test_get_report_large_token_summary(self, mock_chat_filter, mock_summarize, mock_assessment):
        """
        Test that summarize_chat_history is called when content exceeds token limit.
        """
        # 1. Mock Long Chat Data (> 5000 tokens estimated)
        # 4000 words * 1.5 = 6000 tokens
        long_text = "word " * 4000
        mock_chat = MagicMock()
        mock_chat.content = [{"message": long_text}]
    
        mock_chat_filter.return_value = [mock_chat]

        mock_assessment.return_value = {"result": "ok"}
        mock_summarize.return_value = "Summarized content"

        # 2. Run function
        get_report()

        # 3. Assertions
        # Verify summarize was called because tokens > 5000
        self.assertTrue(mock_summarize.called)
        # Verify assessment was called with the summarized data
        self.assertTrue(mock_assessment.called)