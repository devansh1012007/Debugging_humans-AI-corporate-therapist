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
    
'''
def counselor_ai_response(payload):
    # Minimal stub for counselor mode.
    ai_url = os.environ.get('AI_SERVER_URL', 'http://192.168.29.162:11434')
    client = Client(host=ai_url,)#timeout=httpx.Timeout(180.0) 
    try:
        #response_obj = client.chat(model='llama3.2:1b', messages=payload, stream=False)
        
        if hasattr(response_obj, 'message'):
            final_text = response_obj.message.content
        elif isinstance(response_obj, dict):
            final_text = response_obj.get('message', {}).get('content', '')
        else:
            final_text = str(response_obj)

    except Exception as e:
        final_text = f"Error: {str(e)}"

    return {
        "response": final_text
        }
    
'''


'''resp = requests.post(
            "http://127.0.0.1:8001/chat",
            json=payload
)'''