# Ai.py
import requests
import ollama
import os

AI_SERVER_URL = os.getenv('AI_SERVER_URL', 'http://localhost:11434')
AI_CHAT_ENDPOINT = os.getenv('AI_CHAT_ENDPOINT', 'http://26.217.98.105:8001/chat')

def therpy_ai_response(user_prompt, messages_list, user_name):
    # Streaming response using Ollama
    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=messages_list + [{"role": "user", "content": user_prompt}],
            stream=True
        )
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
    except Exception as e:
        yield f"AI Error: {str(e)}"

def consiler_ai_responce(user_prompt, messages_list, user_name):
    # Example using external request if needed, otherwise fallback to Ollama
    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=messages_list + [{"role": "user", "content": user_prompt}],
            stream=True
        )
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
    except Exception as e:
        yield f"AI Error: {str(e)}"


def summarize_chat_history(chat_history):
    pass