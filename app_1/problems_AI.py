# app_1/problems_AI.py
# problems_AI.py
import ollama
import pydantic
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

class userDashboardLister(BaseModel):
    positives : List[positivepoint]
    recommendations : List[recommendation]
    common_problems : List[Problem]

class TeamDashbordLister(BaseModel):
    policy_changes : list[policy_change]
    common_problems : List[Problem]
    recommendations : List[recommendation]

def UserDashboard(chats, exiting_data):
    exiting_data_str = str(exiting_data)
    prompt = f"""   

    Existing Database:
    {exiting_data_str}

    Chat Data to Analyze:
    {chats}

    """
    ai_url = os.environ.get('AI_SERVER_URL', 'http://192.168.29.162:11434')
    client = Client(host=ai_url,)#timeout=httpx.Timeout(180.0) 
    try:
        response_obj = client.chat(model='llama3.2:1b',
                                   messages=[{'role': 'user', 'content': prompt}],
                                   format=userDashboardLister.model_json_schema(),
                                   )
        output = userDashboardLister.model_validate_json(response_obj['message']['content'])
        '''if hasattr(response_obj, 'message'):
            final_text = response_obj.message.content
        elif isinstance(response_obj, dict):
            final_text = response_obj.get('message', {}).get('content', '')
        else:
            final_text = str(response_obj)'''

    except Exception as e:
        output = f"Error: {str(e)}"
    return {
        "content": output
        }

def TeamDashboard(chats, exiting_data):
    exiting_data_str = str(exiting_data)
    prompt = f"""   

    Existing Database:
    {exiting_data_str}

    Chat Data to Analyze:
    {chats}

    """
    ai_url = os.environ.get('AI_SERVER_URL', 'http://192.168.29.162:11434')
    client = Client(host=ai_url,)#timeout=httpx.Timeout(180.0) 
    try:
        response_obj = client.chat(model='llama3.2:1b',
                                   messages=[{'role': 'user', 'content': prompt}],
                                   format=TeamDashbordLister.model_json_schema(),
                                   )
        
        output = TeamDashbordLister.model_validate_json(response_obj['message']['content'])


        '''if hasattr(response_obj, 'message'):
            final_text = response_obj.message.content
        elif isinstance(response_obj, dict):
            final_text = response_obj.get('message', {}).get('content', '')
        else:
            final_text = str(response_obj)
        '''
    except Exception as e:
        output = f"Error: {str(e)}"
    return {
        "content": output
        }















'''
def prob_lister(chat_data, existing_probs):
    # Convert existing problems to a string for the prompt
    existing_str = str(existing_probs)
    
    prompt = f"""
    You are an analytical assistant. 
    1. Analyze the following chat data to identify psychological or lifestyle problems.
    2. Check if these problems already exist in the 'Existing Database' list provided below.
    3. If a problem is NEW, extract a suggestion from the AI's responses in the chat data.
    4. Return the complete updated list of problems (Existing + New).

    Existing Database:
    {existing_str}

    Chat Data to Analyze:
    {chat_data}
    """

    # Using Ollama's structured output capability
    response = ollama.chat(
        model='llama3.2:1b', # Or your preferred model
        messages=[{'role': 'user', 'content': prompt}],
        format=ProblemList.model_json_schema(), # This enforces the pydantic schema
    )

    # Parse the response
    output = ProblemList.model_validate_json(response['message']['content'])
    return output.problems

class teamProblem(BaseModel):
    problems: str
    suggestion: str

class teamProblemList(BaseModel):
    problems: List[teamProblem]

def common_problem_lister(total_team_problems):## team problems 
    existing_str = str(total_team_problems)
    
    prompt = f"""
    You are an analytical assistant. 
    1. Analyze the following chat data to identify psychological or lifestyle problems.
    2. Check if these problems already exist in the 'Existing Database' list provided below.
    3. If a problem is NEW, extract a suggestion from the AI's responses in the chat data.
    4. Return the complete updated list of problems (Existing + New).

    Existing Database:
    {existing_str}

    """

    # Using Ollama's structured output capability
    response = ollama.chat(
        model='llama3.2:1b', # Or your preferred model
        messages=[{'role': 'user', 'content': prompt}],
        format=teamProblemList.model_json_schema(), # This enforces the pydantic schema
    )

    # Parse the response
    output = teamProblemList.model_validate_json(response['message']['content'])
    return output.problems


def positive_points(chats):
    prompt = f"""
    you are analytical assistant, list all the good possitive points about the user but NOT THE ASSISTANT from the given data :
    {chats}
    """
    response = ollama.chat(
        model='llama3.2:1b', 
        messages=[{'role': 'user', 'content': prompt}],
    )
    return response['message']['content']

def policy_changes():
    pass

'''