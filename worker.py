import os, time, sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv
from services.ai_agent import generate_message
from services.whatsapp import send_template_message

load_dotenv()
DB=os.getenv("DATABASE_PATH","ahj.db")
INTERVAL=int(os.getenv("WORKER_INTERVAL_SECONDS","30"))

def run_once():
    # Safe automation: only opted-in contacts with an explicitly queued message.
    # Add your own scheduling/approval policy before enabling autonomous campaigns.
    return 0

if __name__=="__main__":
    print("AHJ AI Agent worker started. No queued campaigns will be sent until configured.")
    while True:
        try: run_once()
        except Exception as e: print("Worker error:", e)
        time.sleep(INTERVAL)
