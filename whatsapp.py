import os, requests

def send_template_message(to: str, body: str) -> dict:
    """
    Official WhatsApp Cloud API adapter.
    For production business-initiated messaging, use an approved WhatsApp
    message template where required by Meta's current messaging rules.
    """
    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    version = os.getenv("WHATSAPP_GRAPH_VERSION", "v23.0")
    if not token or not phone_id:
        raise RuntimeError("WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID are required")

    # This sends a text message only where the current WhatsApp policy/session
    # rules permit it. For template sends, replace the payload with your
    # approved template name + parameters.
    url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    payload = {"messaging_product":"whatsapp","to":to,"type":"text",
               "text":{"preview_url":False,"body":body}}
    r = requests.post(url, headers={"Authorization":f"Bearer {token}",
                                    "Content-Type":"application/json"},
                      json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    mid = ""
    try: mid = data["messages"][0]["id"]
    except Exception: pass
    return {"message_id": mid, "status": "sent", "provider_response": data}
