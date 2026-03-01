# Ai.py
import requests
import ollama
import os
from urllib.parse import urljoin
import requests
import json

def therpy_ai_response(user_prompt, messages_list, user_name):
    AI_SERVER_URL = os.getenv('AI_CHAT_ENDPOINT')
    endpoint = "chat/stream"
    full_url = str(urljoin(AI_SERVER_URL, endpoint))
    full_url = "http://172.25.176.221:8001/chat/stream"
    payload = {
        "message": user_prompt,
        "conversation": messages_list,
        "user_profile": user_name,
        "workspace_context": "the company is in Tamil Nadu, respect it's believes",
        "model_override": "therapy-ai",
    }
    r = requests.post(
        full_url,
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
        endpoint = "chat/stream"
        AI_SERVER_URL = os.getenv('AI_CHAT_ENDPOINT_2')
        full_url = str(urljoin(AI_SERVER_URL, endpoint))
        full_url = "http://172.25.251.52:8001/chat/stream"#172.25.251.52
        r = requests.post(full_url,#"http://172.25.180.142:8001/chat/stream"
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
    endpoint = "/summarizer"
    AI_SERVER_URL = os.getenv('AI_CHAT_ENDPOINT_3')
    full_url = str(urljoin(AI_SERVER_URL, endpoint))
    full_url = "http://172.25.180.142:8001/summarizer"    
    response = requests.post(
        full_url,
        json=payload
    )
    return response.json()["output"]


def personality_extractor(conversations,existing_personality_profile):
    payload = {
        "conversations": conversations,
        "existing_personality_profile": existing_personality_profile
    }
    endpoint = "personality_extractor"
    AI_SERVER_URL = os.getenv('AI_CHAT_ENDPOINT_4')
    full_url = str(urljoin(AI_SERVER_URL, endpoint))
    full_url = "http://172.25.180.142:8001/personality_extractor"
    response = requests.post(
        full_url,
        json = payload
    )
    return response.json()["output"]


def assesment(existing_profile,conversations):
    payload = {
        "prev_ass": existing_profile,
        "convo": conversations,    
    }
    endpoint = "assessments"
    AI_SERVER_URL = os.getenv('AI_CHAT_ENDPOINT_5')
    full_url = str(urljoin(AI_SERVER_URL, endpoint))
    
    response = requests.post(
        full_url,
        json = payload
    )
    response.raise_for_status()
    return response.json()["result"]