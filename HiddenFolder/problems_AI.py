# problems_AI.py
"""
AI functions for generating team and user dashboard data
"""
import json
import requests
from typing import List, Dict, Any


# ============================================================================
# AI PROMPTS
# ============================================================================

TEAM_DASHBOARD_PROMPT = """You are an organizational psychologist and HR analyst. 

You will receive:
1. A list of chat summaries from team members
2. Existing team data (if any) from previous analyses

Your task is to analyze the team's collective mental health, workplace issues, and needs.

CRITICAL: You MUST respond with ONLY a valid JSON object. No explanations, no preamble, no markdown formatting, no ```json``` tags. Just the raw JSON object.

The JSON structure must be EXACTLY:
{{
    "policy_changes": [
        {{
            "title": "Brief policy title",
            "description": "Detailed description of the policy change needed"
        }}
    ],
    "common_problems": [
        {{
            "problem": "Short problem name",
            "description": "Detailed description of the problem affecting the team"
        }}
    ],
    "recommendations": [
        {{
            "recommendation": "Specific actionable recommendation for leadership"
        }}
    ]
}}

ANALYSIS GUIDELINES:
1. **policy_changes**: Identify needed organizational policies (3-8 items)
   - Focus on preventive measures and cultural changes
   
2. **common_problems**: Identify recurring themes across team members (3-8 items)
   - Include severity indicators in descriptions
   
3. **recommendations**: Provide actionable next steps for managers (3-8 items)
   - Each should be specific and implementable

Now analyze the following data:
Chat summaries: {chats}
Existing team data: {existing_data}

Remember: Return ONLY the JSON object, nothing else."""


USER_DASHBOARD_PROMPT = """You are a personal mental health and wellness counselor.

You will receive:
1. A list of chat summaries from a user's therapy/counseling sessions
2. Existing personal data (if any) from previous analyses

Your task is to provide a personal mental health dashboard for this individual.

CRITICAL: You MUST respond with ONLY a valid JSON object. No explanations, no preamble, no markdown formatting, no ```json``` tags. Just the raw JSON object.

The JSON structure must be EXACTLY:
{{
    "positives": [
        {{
            "positive": "A positive observation about the person's mental health, coping strategies, or growth"
        }}
    ],
    "common_problems": [
        {{
            "problem": "Short problem name",
            "description": "Detailed description of the challenge this person is facing"
        }}
    ],
    "recommendations": [
        {{
            "recommendation": "Specific, actionable recommendation for personal wellbeing improvement"
        }}
    ]
}}

ANALYSIS GUIDELINES:
1. **positives**: Highlight strengths and progress (3-6 items)
2. **common_problems**: Identify recurring personal challenges (3-8 items)
3. **recommendations**: Provide personalized strategies (5-10 items)

Now analyze the following data:
Chat summaries: {chats}
Existing personal data: {existing_data}

Remember: Return ONLY the JSON object, nothing else."""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clean_json_response(response_text: str) -> str:
    """
    Clean AI response to extract pure JSON
    Removes markdown code blocks, extra whitespace, etc.
    """
    # Remove markdown code blocks
    response_text = response_text.strip()
    
    # Remove ```json and ``` markers
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    
    return response_text.strip()


def validate_team_dashboard_structure(data: Dict[str, Any]) -> bool:
    """
    Validate that the team dashboard data has correct structure
    """
    required_keys = ['policy_changes', 'common_problems', 'recommendations']
    
    if not all(key in data for key in required_keys):
        return False
    
    # Validate each is a list
    if not all(isinstance(data[key], list) for key in required_keys):
        return False
    
    # Validate policy_changes structure
    for item in data['policy_changes']:
        if not isinstance(item, dict):
            return False
        if 'title' not in item or 'description' not in item:
            return False
    
    # Validate common_problems structure
    for item in data['common_problems']:
        if not isinstance(item, dict):
            return False
        if 'problem' not in item or 'description' not in item:
            return False
    
    # Validate recommendations structure
    for item in data['recommendations']:
        if not isinstance(item, dict):
            return False
        if 'recommendation' not in item:
            return False
    
    return True


def validate_user_dashboard_structure(data: Dict[str, Any]) -> bool:
    """
    Validate that the user dashboard data has correct structure
    """
    required_keys = ['positives', 'common_problems', 'recommendations']
    
    if not all(key in data for key in required_keys):
        return False
    
    # Validate each is a list
    if not all(isinstance(data[key], list) for key in required_keys):
        return False
    
    # Validate positives structure
    for item in data['positives']:
        if not isinstance(item, dict):
            return False
        if 'positive' not in item:
            return False
    
    # Validate common_problems structure
    for item in data['common_problems']:
        if not isinstance(item, dict):
            return False
        if 'problem' not in item or 'description' not in item:
            return False
    
    # Validate recommendations structure
    for item in data['recommendations']:
        if not isinstance(item, dict):
            return False
        if 'recommendation' not in item:
            return False
    
    return True


# ============================================================================
# MAIN AI FUNCTIONS
# ============================================================================

def TeamDashboard_data(chats: List[str], exiting_data: List[Dict]) -> Dict[str, Any]:
    """
    Generate team dashboard data from chat summaries
    
    Args:
        chats: List of chat summaries from team members
        exiting_data: Existing team data from previous analyses
    
    Returns:
        Dictionary with policy_changes, common_problems, and recommendations
    """
    # Format the prompt with actual data
    prompt = TEAM_DASHBOARD_PROMPT.format(
        chats=json.dumps(chats, indent=2),
        existing_data=json.dumps(exiting_data, indent=2)
    )
    
    try:
        # Send to AI endpoint
        # ADJUST THIS URL TO MATCH YOUR AI SERVER
        response = requests.post(
            "http://172.25.184.106:8001/chat",
            json={
                "message": prompt,
                "conversation": [],
                "model_override": "problem-solver"  # or whatever model you use
            },
            timeout=60
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # Extract the AI's message
        if 'message' in response_data and 'content' in response_data['message']:
            ai_text = response_data['message']['content']
        elif 'output' in response_data:
            ai_text = response_data['output']
        else:
            ai_text = response_data.get('response', str(response_data))
        
        # Clean and parse JSON
        clean_text = clean_json_response(ai_text)
        result = json.loads(clean_text)
        
        # Validate structure
        if not validate_team_dashboard_structure(result):
            raise ValueError("AI response has invalid structure")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"ERROR: AI returned invalid JSON: {e}")
        print(f"AI Response: {ai_text[:500]}...")
        # Return empty structure as fallback
        return {
            "policy_changes": [],
            "common_problems": [],
            "recommendations": []
        }
    
    except Exception as e:
        print(f"ERROR in TeamDashboard_data: {e}")
        # Return empty structure as fallback
        return {
            "policy_changes": [],
            "common_problems": [],
            "recommendations": []
        }


def UserDashboard_data(chats: List[str], existing_data: List[Dict]) -> Dict[str, Any]:
    """
    Generate user dashboard data from chat summaries
    
    Args:
        chats: List of chat summaries from user's sessions
        existing_data: Existing personal data from previous analyses
    
    Returns:
        Dictionary with positives, common_problems, and recommendations
    """
    # Format the prompt with actual data
    prompt = USER_DASHBOARD_PROMPT.format(
        chats=json.dumps(chats, indent=2),
        existing_data=json.dumps(existing_data, indent=2)
    )
    
    try:
        # Send to AI endpoint
        # ADJUST THIS URL TO MATCH YOUR AI SERVER
        response = requests.post(
            "http://172.25.184.106:8001/chat",
            json={
                "message": prompt,
                "conversation": [],
                "model_override": "therapist"  # or whatever model you use
            },
            timeout=60
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # Extract the AI's message
        if 'message' in response_data and 'content' in response_data['message']:
            ai_text = response_data['message']['content']
        elif 'output' in response_data:
            ai_text = response_data['output']
        else:
            ai_text = response_data.get('response', str(response_data))
        
        # Clean and parse JSON
        clean_text = clean_json_response(ai_text)
        result = json.loads(clean_text)
        
        # Validate structure
        if not validate_user_dashboard_structure(result):
            raise ValueError("AI response has invalid structure")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"ERROR: AI returned invalid JSON: {e}")
        print(f"AI Response: {ai_text[:500]}...")
        # Return empty structure as fallback
        return {
            "positives": [],
            "common_problems": [],
            "recommendations": []
        }
    
    except Exception as e:
        print(f"ERROR in UserDashboard_data: {e}")
        # Return empty structure as fallback
        return {
            "positives": [],
            "common_problems": [],
            "recommendations": []
        }


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

if __name__ == "__main__":
    """Test the AI functions with sample data"""
    
    print("="*70)
    print("TESTING AI FUNCTIONS")
    print("="*70)
    
    # Test data
    sample_chats = [
        "User discussed feeling overwhelmed with work deadlines and constant meetings",
        "User mentioned difficulty sleeping due to stress about upcoming presentation",
        "User expressed satisfaction with new meditation routine helping with anxiety"
    ]
    
    sample_team_chats = [
        "Employee A mentioned burnout from excessive meetings",
        "Employee B discussed lack of collaboration between departments",
        "Employee C expressed need for more mental health support"
    ]
    
    print("\n" + "-"*70)
    print("TEST 1: UserDashboard_data")
    print("-"*70)
    
    user_result = UserDashboard_data(sample_chats, [])
    print(json.dumps(user_result, indent=2))
    
    print("\n" + "-"*70)
    print("TEST 2: TeamDashboard_data")
    print("-"*70)
    
    team_result = TeamDashboard_data(sample_team_chats, [])
    print(json.dumps(team_result, indent=2))
    
    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)
