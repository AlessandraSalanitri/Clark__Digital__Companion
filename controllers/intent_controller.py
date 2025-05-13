from assistant.intent_router import detect_intent

def get_intent_from_prompt(prompt: str) -> str:
    try:
        return detect_intent(prompt)
    except Exception as e:
        print("[Intent Detection Error]:", e)
        return "chat"  # fallback
