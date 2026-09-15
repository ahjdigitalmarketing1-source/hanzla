import os, sqlite3, json
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from dotenv import load_dotenv
from services.ai_agent import generate_message
from services.whatsapp import send_template_message

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me")
DB = os.getenv("DATABASE_PATH", "ahj.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS contacts(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      phone TEXT NOT NULL UNIQUE,
      opted_in INTEGER NOT NULL DEFAULT 0,
      status TEXT NOT NULL DEFAULT 'Pending',
      notes TEXT DEFAULT '',
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS messages(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contact_id INTEGER NOT NULL,
      direction TEXT NOT NULL,
      body TEXT NOT NULL,
      provider_id TEXT DEFAULT '',
      status TEXT DEFAULT 'queued',
      created_at TEXT NOT NULL,
      FOREIGN KEY(contact_id) REFERENCES contacts(id)
    );
    CREATE TABLE IF NOT EXISTS settings(
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
    """)
    con.commit(); con.close()

@app.route("/")
def index():
    con = db()
    contacts = con.execute("SELECT * FROM contacts ORDER BY id DESC").fetchall()
    stats = {
        "contacts": con.execute("SELECT COUNT(*) FROM contacts").fetchone()[0],
        "opted_in": con.execute("SELECT COUNT(*) FROM contacts WHERE opted_in=1").fetchone()[0],
        "sent": con.execute("SELECT COUNT(*) FROM messages WHERE direction='outbound'").fetchone()[0],
        "replies": con.execute("SELECT COUNT(*) FROM messages WHERE direction='inbound'").fetchone()[0],
    }
    con.close()
    return render_template("index.html", contacts=contacts, stats=stats)

@app.post("/contacts")
def add_contact():
    name = request.form.get("name","").strip()
    phone = request.form.get("phone","").strip()
    opted_in = 1 if request.form.get("opted_in") == "1" else 0
    if not name or not phone:
        flash("Name and phone are required.")
        return redirect(url_for("index"))
    con = db()
    try:
        con.execute("INSERT INTO contacts(name,phone,opted_in,created_at) VALUES(?,?,?,?)",
                    (name, phone, opted_in, datetime.now(timezone.utc).isoformat()))
        con.commit()
        flash("Contact added.")
    except sqlite3.IntegrityError:
        flash("That phone number already exists.")
    finally:
        con.close()
    return redirect(url_for("index"))

@app.post("/ai/generate")
def ai_generate():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt","").strip()
    if not prompt:
        return jsonify(error="Prompt is required."), 400
    try:
        return jsonify(result=generate_message(prompt))
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.post("/send/<int:contact_id>")
def send(contact_id):
    con = db()
    contact = con.execute("SELECT * FROM contacts WHERE id=?", (contact_id,)).fetchone()
    con.close()
    if not contact:
        return jsonify(error="Contact not found."), 404
    if not contact["opted_in"]:
        return jsonify(error="This contact is not marked as opted-in."), 400
    body = request.form.get("message","").strip()
    if not body:
        return jsonify(error="Message is required."), 400
    try:
        result = send_template_message(contact["phone"], body)
        con = db()
        con.execute("""INSERT INTO messages(contact_id,direction,body,provider_id,status,created_at)
                       VALUES(?,?,?,?,?,?)""",
                    (contact_id, "outbound", body, result.get("message_id",""),
                     result.get("status","sent"), datetime.now(timezone.utc).isoformat()))
        con.execute("UPDATE contacts SET status='Contacted' WHERE id=?", (contact_id,))
        con.commit(); con.close()
        return jsonify(ok=True, result=result)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.post("/webhook")
def webhook():
    # WhatsApp Cloud API webhook receiver.
    payload = request.get_json(silent=True) or {}
    # Production: validate X-Hub-Signature-256 and parse all incoming events.
    # This demo parser records plain inbound text when the standard fields exist.
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []) or []:
                    sender = msg.get("from")
                    text = (msg.get("text") or {}).get("body")
                    if sender and text:
                        con = db()
                        c = con.execute("SELECT id FROM contacts WHERE phone=?", (sender,)).fetchone()
                        if c:
                            con.execute("""INSERT INTO messages(contact_id,direction,body,status,created_at)
                                           VALUES(?,?,?,?,?)""",
                                        (c["id"],"inbound",text,"received",
                                         datetime.now(timezone.utc).isoformat()))
                            con.commit()
                        con.close()
        return "EVENT_RECEIVED", 200
    except Exception:
        return "EVENT_RECEIVED", 200

@app.get("/health")
def health():
    return {"ok": True, "service": "AHJ Group AI Agent"}

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")), debug=os.getenv("DEBUG","false").lower()=="true")
