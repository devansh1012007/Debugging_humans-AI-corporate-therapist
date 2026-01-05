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
    client = Client(host='http://192.168.1.20:11434',)#timeout=httpx.Timeout(180.0) 
    response = client.chat(model='llama3.2:1b', messages=history, prompt=prompt)
    #print("Raw response:", response)
    reply = None
    if isinstance(response, dict):
        if 'message' in response and isinstance(response['message'], dict):
            reply = response['message'].get('content')
        elif 'choices' in response and response['choices']:
            first = response['choices'][0]
            reply = (first.get('message', {}) or {}).get('content') or first.get('text') or first.get('content')
        else:
            reply = response.get('text') or response.get('content') or str(response)
    else:
        # Try common attributes on response objects
        for attr in ('message', 'response', 'text', 'content'):
            val = getattr(response, attr, None)
            if val:
                reply = val
                break
        if reply is None:
            import re
            m = re.search(r'response=\"([^\"]+)\"', str(response))
            if m:
                reply = m.group(1)
            else:
                reply = str(response)


    return {"message": {"role": "assistant", "response": reply}}
