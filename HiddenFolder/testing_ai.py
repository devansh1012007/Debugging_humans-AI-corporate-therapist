from ollama import Client
import ollama
import httpx

# Minimal stub: returns a dict with a `message` mapping containing `response`.
# Real implementation should call an AI service here.
# Replace with the actual IP address of your AI server
# Port 11434 is the default for Ollama
prompt = "Hello, how are you?"
history = [{"role": "user", "content": prompt}]
client = Client(host='http://192.168.1.20:11434',
                )#timeout=httpx.Timeout(180.0) 
response = client.generate(model='llama3.2:1b', prompt=prompt)
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

print("Therapy AI response:", reply)

