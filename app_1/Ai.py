#AI.py
from ollama import Client
import httpx
import os
def therpy_ai_response(prompt, history):
    # Minimal stub: returns a dict with a `message` mapping containing `response`.
    # Real implementation should call an AI service here.
    # Replace with the actual IP address of your AI server
    # Port 11434 is the default for Ollama
    
    ai_url = os.environ.get('AI_SERVER_URL', 'http://192.168.1.20:11434')
    client = Client(host=ai_url,)#timeout=httpx.Timeout(180.0) 
    try:
        response_obj = client.chat(model='llama3.2:1b', messages=history, stream=False)
        
        if hasattr(response_obj, 'message'):
            final_text = response_obj.message.content
        elif isinstance(response_obj, dict):
            final_text = response_obj.get('message', {}).get('content', '')
        else:
            final_text = str(response_obj)

    except Exception as e:
        final_text = f"Error: {str(e)}"

    return {
        "message": {
            "role": "assistant", 
            "content": final_text 
        }
    }

def counselor_ai_responce(prompt, history):
    # Minimal stub for counselor mode.
    ai_url = os.environ.get('AI_SERVER_URL', 'http://192.168.1.20:11434')
    client = Client(host=ai_url,)#timeout=httpx.Timeout(180.0) 
    try:
        response_obj = client.chat(model='llama3.2:1b', messages=history, stream=False)
        
        if hasattr(response_obj, 'message'):
            final_text = response_obj.message.content
        elif isinstance(response_obj, dict):
            final_text = response_obj.get('message', {}).get('content', '')
        else:
            final_text = str(response_obj)

    except Exception as e:
        final_text = f"Error: {str(e)}"

    return {
        "message": {
            "role": "assistant", 
            "content": final_text 
        }
    }