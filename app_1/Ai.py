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
        response_obj = requests.post("http://192.168.29.162:8001/chat",json=payload)# 26.217.98.105 --> vpn

    except Exception as e:
        final_text = f"Error: {str(e)}"
    data = response_obj.json()
    print("AI Response Data:", data)
    #print(f"Status Code: {response_obj.status_code}")
    #print(f"Raw Response Content: {response_obj.text}")
    return data
    
