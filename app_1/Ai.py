# Ai.py
import requests
import ollama
import os

AI_SERVER_URL = os.getenv('AI_CHAT_ENDPOINT', 'http://localhost:11434')
#AI_CHAT_ENDPOINT = os.getenv('AI_CHAT_ENDPOINT', 'http://26.217.98.105:8001/chat')

def therpy_ai_response(user_prompt, messages_list, user_name):
    # Streaming response using Ollama
    try:
        response = requests.post("http://26.80.229.208:8001/chat/stream",
            json={
            "message": user_prompt,
            "conversation": messages_list,
            "user_profile":user_name,
            "workspace_context":"",
                },
            stream=True
        )
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content'] # might need to chage it but maybe not
    except Exception as e:
        yield f"AI Error: {str(e)}"


def consiler_ai_responce(user_prompt, messages_list, user_name):
    # Example using external request if needed, otherwise fallback to Ollama
    try:
        response = requests.post("http://26.80.229.208:8001/chat/stream",
            json={
            "message": user_prompt,
            "conversation": messages_list,
            "user_profile":user_name,
            "workspace_context":"",
            "model_override": "problem-solver"
                },
            stream=True
        )
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
    except Exception as e:
        yield f"AI Error: {str(e)}"


def summarize_chat_history(conversations):
    payload = {
    "conversation": conversations
    }

    response = requests.post(
        "http://26.80.229.208:8001/summarizer",
        json=payload
    )
    return response.json()["output"]


def personality_extractor(conversations,existing_personality_profile):
    payload = {
        "conversations": conversations,
        "existing_personality_profile": existing_personality_profile
    }

    response = requests.post(
        "http://26.80.229.208:8001/personality_extractor",
        json = payload
    )
    return response.json()["output"]

"""
#AI.py
#from ollama import Client
import httpx
import requests
import os
def ai_response(payload):
      
    #ai_url = os.environ.get('AI_SERVER_URL', 'http://192.168.29.162:11434',)##'http://192.168.1.20:11434'--> ram    #http://192.168.29.162:11434 --> devansh
    #client = Client(host=ai_url,)#timeout=httpx.Timeout(180.0) 
    try:
        #response_obj = client.chat(model='llama3.2:1b', messages=history, stream=False)
        response_obj = requests.post("http://26.217.98.105:8001/chat",json=payload)# 26.217.98.105 --> vpn

    except Exception as e:
        final_text = f"Error: {str(e)}"
    data = response_obj.json()
    #print(f"Status Code: {response_obj.status_code}")
    #print(f"Raw Response Content: {response_obj.text}")
    return data

"""




