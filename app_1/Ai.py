def therpy_ai_response(prompt, history):
    # Minimal stub: returns a dict with a `message` mapping containing `response`.
    # Real implementation should call an AI service here.
    reply = f"[therapy] Simulated reply to: {prompt}"
    return {"message": {"response": reply, "role": "assistant", "content": reply}}


def consiler_ai_responce(prompt, history):
    # Minimal stub for consiler mode.
    reply = f"[consiler] Simulated reply to: {prompt}"
    return {"message": {"response": reply, "role": "assistant", "content": reply}}
