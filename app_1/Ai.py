# Ai.py
import requests
import ollama
import os

AI_SERVER_URL = os.getenv('AI_CHAT_ENDPOINT', 'http://localhost:11434')
#AI_CHAT_ENDPOINT = os.getenv('AI_CHAT_ENDPOINT', 'http://26.217.98.105:8001/chat')
import requests
import json

def therpy_ai_response(user_prompt, messages_list, user_name):
   
    payload = {
        "message": user_prompt,
        "conversation": messages_list,
        "user_profile": user_name,
        "workspace_context": "the company is in Tamil Nadu, respect it's believes",
        "model_override": "therapy-ai",
    }
    r = requests.post(
        "http://172.25.188.183:8001/chat/stream",
        json=payload,
        stream=True,
        #timeout=30 
    )
    
    
    
    for line in r.iter_lines():
        if not line:
            continue

        event = json.loads(line.decode("utf-8").replace("data: ", ""))

        if event["type"] == "meta":
            print("\n[METADATA]")
            print(event["data"])
            print("\n--- RESPONSE ---\n")

        elif event["type"] == "token":
            yield event["data"]

        elif event["type"] == "done":
            print("\n\n[STREAM COMPLETE]")
            break

        elif event["type"] == "error":
            print("\n[ERROR]", event["message"])
            break    

def consiler_ai_responce(user_prompt, messages_list, user_name):
        payload = {
        "message": user_prompt,
        "conversation": messages_list, # Creates a shallow copy
        "user_profile": user_name,
        "workspace_context": "the company is in Tamil Nadu, respect it's believes",
        "model_override": "problem-solver",
    }
        r = requests.post("http://172.25.188.183:8001/chat/stream",
            json=payload,
            stream=True
        )
        for line in r.iter_lines():
            if not line:
                continue
            event = json.loads(line.decode("utf-8").replace("data: ", ""))
            if event["type"] == "token":
                yield event["data"]
            


def summarize_chat_history(conversations):
    payload = {
    "conversation": conversations
    }

    response = requests.post(
        "http://172.25.188.183:8001/summarizer",
        json=payload
    )
    return response.json()["output"]


def personality_extractor(conversations,existing_personality_profile):
    payload = {
        "conversations": conversations,
        "existing_personality_profile": existing_personality_profile
    }

    response = requests.post(
        "http://172.25.188.183:8001/personality_extractor",
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

def assesment(existing_profile,conversations):
    payload = {
        "prev_ass": existing_profile,
        "convo": conversations,
        
    }

    response = requests.post(
        "http://172.25.188.183:8001/assessments",
        json = payload
    )
    response.raise_for_status()
    return response.json()["result"]