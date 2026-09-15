import os, requests

def generate_message(instruction: str) -> str:
    api_key = os.getenv("AI_API_KEY")
    base = os.getenv("AI_API_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("AI_MODEL", "gpt-4.1-mini")
    if not api_key:
        raise RuntimeError("AI_API_KEY is not configured in .env")

    system = (
        "You are the AHJ Group outreach assistant. Write concise, professional, "
        "non-deceptive business messages. Never claim a relationship that does not exist. "
        "Do not generate spam tactics, evasion instructions, or messages intended to bypass "
        "WhatsApp policies. Respect opt-out requests."
    )
    r = requests.post(
        base.rstrip("/") + "/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "temperature": 0.5,
              "messages":[{"role":"system","content":system},{"role":"user","content":instruction}]},
        timeout=60
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()
