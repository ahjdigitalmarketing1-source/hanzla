# AHJ Group — AI Agent v2

A production-oriented starter architecture for an AI-assisted WhatsApp Business outreach dashboard.

## Included
- Flask web dashboard, mobile responsive
- SQLite contact/message database
- Opt-in flag on every contact
- AI message-generation adapter
- Official WhatsApp Cloud API adapter
- Incoming WhatsApp webhook endpoint
- Background-worker foundation
- Environment-based secrets
- Health endpoint

## Run locally
1. Install Python 3.11+.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Put your own AI and WhatsApp Business API credentials in `.env`.
5. Run `python app.py`.
6. Open `http://127.0.0.1:5000`.

## Important production setup
- Create/configure your Meta WhatsApp Business Platform app and webhook.
- Use approved WhatsApp message templates for business-initiated conversations when required.
- Collect and honor recipient opt-in and opt-out.
- Configure webhook signature verification before exposing `/webhook` publicly.
- Use HTTPS in production.
- Replace the demo worker with a real queue/scheduler (Celery/RQ/APScheduler + Redis/Postgres are suitable).
- Store secrets in environment/secret management, never in source control.
- Add authentication, rate limits, audit logs, retries, idempotency, and monitoring before deployment.

The software does NOT scrape Google Maps, harvest phone numbers, or bypass WhatsApp restrictions.
