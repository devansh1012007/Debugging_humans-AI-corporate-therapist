# app_1/problems_AI.py
# problems_AI.py
import ollama
import pydantic

# example chat data
# [{"Prompt": "I feel tired", "Response": "Can you explain more?"},{"Prompt": "I am jsut drained from work and I feel like there is nothing to lean on", "Response": "Why do you feel this way?"}]
#example of exiting problem 
# exiting problems = [{problem : highly stressed, suggestion : u should take breaks and practice 1,2,3,4,5}, {problem : overwork, suggestion : set boundries}]
# i will give ai chat data and say assess the problems in the chat and check if that problem already exits in db, if not add the problem with suggestion to improve from the Response that ai has given and return me the list of prob 
# Example output = [{problem : highly stressed, suggestion : u should take breaks and practice 1,2,3,4,5}, {problem : overwork, suggestion : set boundries}, {problem : loneliness, suggestion : join social groups and engage more with people}]
from typing import List
from pydantic import BaseModel
# this will be updated  soon
class Problem(BaseModel):
    problem: str
    suggestion: str

class ProblemList(BaseModel):
    problems: List[Problem]

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

def common_problem_lister(total_team_problems):
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


def team_summary(abt_user):
    prompt = f"""
    You are an analytical assistant. 
    1. Analyze the following chat data to provide a concise summary of the team's overall psychological and lifestyle challenges.
    2. Provide actionable recommendations to address these challenges.

    Chat Data to Analyze:
    {abt_user}
    """

    response = ollama.chat(
        model='llama3.2:1b', 
        messages=[{'role': 'user', 'content': prompt}],
    )

    return response['message']['content']