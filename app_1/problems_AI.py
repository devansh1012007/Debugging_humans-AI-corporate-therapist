from ollama import Client
import os
from typing import List
from pydantic import BaseModel
# this will be updated  soon
class Problem(BaseModel):
    problem: str
    description: str

class positivepoint(BaseModel):
    positive: str

class positivepointlister(BaseModel):
    positives : list[positivepoint]

class recommendation(BaseModel):
    recommendation : str

class recommendationsLister(BaseModel):
    recommendations : list[recommendation]

class ProblemList(BaseModel):
    common_problems: List[Problem]

class policy_change(BaseModel):
    title : str
    description : str

class policy_changesLister(BaseModel):
    policy_changes : list[policy_change]

class Note(BaseModel):
    note : str
class userDashboardLister(BaseModel):
    positives : List[positivepoint]
    recommendations : List[recommendation]
    common_problems : List[Problem]
    Notes_for_self : List[Note]

class TeamDashbordLister(BaseModel):
    policy_changes : list[policy_change]
    common_problems : List[Problem]
    recommendations : List[recommendation]

def UserDashboard_data(chats, exiting_data):
    exiting_data_str = str(exiting_data)
    prompt = """   
    You are a personal mental health and wellness counselor.

    You will receive:
    1. A list of chat summaries from a user's therapy/counseling sessions
    2. Existing personal data (if any) from previous analyses

    Your task is to provide a personal mental health dashboard for this individual.

    CRITICAL: You MUST respond with ONLY a valid JSON object. No explanations, no preamble, no markdown formatting, no ```json``` tags. Just the raw JSON object.

    The JSON structure must be EXACTLY:
    [{
        "positives": [
            {
                "positive": "A positive observation about the person's mental health, coping strategies, or growth"
            }
        ],
        "common_problems": [
            {
                "problem": "Short problem name",
                "description": "Detailed description of the challenge this person is facing"
            }
        ],
        "recommendations": [
            {
                "recommendation": "Specific, actionable recommendation for personal wellbeing improvement"
            }
        ],
        "Notes_for_self": [
        {
            "note":"add data you whould like to tell the ai who is going to work on the next data set"
        }
        ]
    }]

    ANALYSIS GUIDELINES:
    1. **positives**: Highlight strengths and progress (3-6 items)
    2. **common_problems**: Identify recurring personal challenges (3-8 items)
    3. **recommendations**: Provide personalized strategies (5-10 items)
    """ +f"""
    Now analyze the following data:
    Chat summaries: {chats}
    Existing personal data: {exiting_data_str}

    Remember: Return ONLY the JSON object, nothing else.
    """
    ai_url = os.environ.get('AI_CHAT_ENDPOINT_6',)
    client = Client(host=ai_url)#timeout=httpx.Timeout(180.0) 
    try:
        response_obj = client.chat(model='qwen2.5:3b-instruct',
                                   messages=[{'role': 'user', 'content': prompt}],
                                   format=userDashboardLister.model_json_schema(),
                                   )
        output = userDashboardLister.model_validate_json(response_obj['message']['content'])


    except Exception as e:
        output = f"Error: {str(e)}"
    return output

def TeamDashboard_data(chats, exiting_data):
    exiting_data_str = str(exiting_data)
    prompt = """   
    You are an organizational psychologist and HR analyst. 

    You will receive:
    1. A list of problems faced by team members, along with solotion and there positives
    2. Ignore the possitive qualities and use the other data
    3. Existing team data (if any) from previous analyses

    Your task is to analyze the team's collective mental health, workplace issues, and needs.

    CRITICAL: You MUST respond with ONLY a valid JSON object. No explanations, no preamble, no markdown formatting, no ```json``` tags. Just the raw JSON object.

    The JSON structure must be EXACTLY:
    {
        "policy_changes": 
            [{
                "title": "Brief policy title",
                "description": "Detailed description of the policy change needed"
            }]
        ,
        "common_problems": 
            [{
                "problem": "Short problem name",
                "description": "Detailed description of the problem affecting the team"
            }]
        ,
        "recommendations": 
            [{
                "recommendation": "Specific actionable recommendation for leadership"
            }]
                
    }

    ANALYSIS GUIDELINES:
    1. **policy_changes**: Identify needed organizational policies (3-8 items)
       - Focus on preventive measures and cultural changes.(give more emphasise more on CULTURAL CHANGES )
    
    2. **common_problems**: Identify recurring themes across team members (3-8 items)
       - Include severity indicators in descriptions
    
    3. **recommendations**: Provide actionable next steps for managers (3-8 items)
       - Each should be specific and implementable
    """+f"""
    Now analyze the following data:
    list of exiting problems and solutions of all the employees : {chats}
    Existing team data: {exiting_data_str}

    Remember: Return ONLY the JSON object, nothing else.
    """
    ai_url = os.environ.get('AI_CHAT_ENDPOINT_6')#'http://172.25.188.183:11434'
    client = Client(host=ai_url,)#timeout=httpx.Timeout(180.0) 
    try:
        response_obj = client.chat(model='qwen2.5:3b-instruct',
                                   messages=[{'role': 'user', 'content': prompt}],
                                   format=TeamDashbordLister.model_json_schema(),
                                   )
        
        output = TeamDashbordLister.model_validate_json(response_obj['message']['content'])

    except Exception as e:
        output = f"Error: {str(e)}"
    return output
