#AI.py
#from ollama import Client
import httpx
import requests
import ollama
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
    print("AI Response Data:", data)
    #print(f"Status Code: {response_obj.status_code}")
    #print(f"Raw Response Content: {response_obj.text}")
    return data
# Ai.py

def therpy_ai_response(user_prompt, messages_list):
    response = ollama.chat(
        model="llama3.2:1b",
        messages=messages_list + [{"role": "user", "content": user_prompt}],
        stream=True 
    )

    for chunk in response:
        # Ollama returns a dictionary, not an object with .choices
        if 'message' in chunk and 'content' in chunk['message']:
            token = chunk['message']['content']
            print(f"DEBUG TOKEN: {token}") # This will show in your terminal
            yield token

def consiler_ai_responce(user_prompt, messages_list):
    response = ollama.chat(
        model="llama3.2:1b",
        messages=messages_list + [{"role": "user", "content": user_prompt}],
        stream=True
    )

    for chunk in response:
        if 'message' in chunk and 'content' in chunk['message']:
            yield chunk['message']['content']