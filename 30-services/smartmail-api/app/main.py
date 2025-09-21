# repo: smartnet-pod-golden
# path: 30-services/smartmail-api/app/main.py
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import os, uuid, datetime
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/smartnet")

app = FastAPI(title="SmartMail API", version="0.1.0")

def conn():
    return psycopg.connect(DATABASE_URL, autocommit=True)

class SendInternalBody(BaseModel):
    to_usernames: List[str] = Field(..., min_items=1)
    subject: str = Field("", max_length=255)
    body: str = Field(..., max_length=20000)

class SendExternalBody(BaseModel):
    to_emails: List[str] = Field(..., min_items=1)
    subject: str
    body_html: str

@app.get("/health")
def health():
    with conn() as c:
        with c.cursor() as cur:
            cur.execute("select 1;")
            return {"ok": True}

def _get_user_id(cur, username:str) -> uuid.UUID:
    cur.execute("select id from users where username=%s;", (username,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"user not found: {username}")
    return row[0]

@app.post("/v1/smartmail/send_internal")
def send_internal(payload: SendInternalBody, x_user: Optional[str] = Header(None, convert_underscores=True)):
    """Internal SmartMail: username→username only (no outside)."""
    if not x_user:
        raise HTTPException(401, "missing X-User header (sender username)")
    with conn() as c, c.cursor() as cur:
        sender_id = _get_user_id(cur, x_user)
        # validate recipients
        rec_ids = []
        for uname in payload.to_usernames:
            rec_ids.append(_get_user_id(cur, uname))
        thread_id = uuid.uuid4()
        msg_id = uuid.uuid4()
        now = datetime.datetime.utcnow()
        cur.execute("""
            insert into smartmail_thread(id, created_at, created_by) values (%s, %s, %s);
        """, (thread_id, now, sender_id))
        cur.execute("""
            insert into smartmail_message(id, thread_id, sender_id, subject, body, created_at)
            values (%s, %s, %s, %s, %s, %s);
        """, (msg_id, thread_id, sender_id, payload.subject, payload.body, now))
        # mailbox copies
        # sender copy → SENT
        cur.execute("""
            insert into smartmail_recipient(message_id, user_id, folder, is_read, created_at)
            values (%s, %s, 'sent', true, %s);
        """, (msg_id, sender_id, now))
        # recipient copies → INBOX
        for rid in rec_ids:
            cur.execute("""
                insert into smartmail_recipient(message_id, user_id, folder, is_read, created_at)
                values (%s, %s, 'inbox', false, %s);
            """, (msg_id, rid, now))
        return {"ok": True, "thread_id": str(thread_id), "message_id": str(msg_id)}

@app.get("/v1/smartmail/mailbox")
def mailbox(folder: str = Query("inbox", pattern="^(inbox|sent|trash)$"),
            limit: int = 20, offset: int = 0,
            x_user: Optional[str] = Header(None, convert_underscores=True)):
    if not x_user: raise HTTPException(401, "missing X-User")
    with conn() as c, c.cursor() as cur:
        uid = _get_user_id(cur, x_user)
        cur.execute("""
        select m.id, m.thread_id, m.subject, left(m.body, 280) as snippet,
               m.created_at, u.username as sender
        from smartmail_recipient r
        join smartmail_message m on m.id = r.message_id
        join users u on u.id = m.sender_id
        where r.user_id = %s and r.folder = %s
        order by m.created_at desc
        limit %s offset %s;
        """, (uid, folder, limit, offset))
        rows = cur.fetchall()
        return [{"message_id": str(r[0]), "thread_id": str(r[1]), "subject": r[2],
                 "snippet": r[3], "created_at": r[4].isoformat()+"Z", "from": r[5]} for r in rows]

@app.get("/v1/smartmail/thread/{thread_id}")
def thread(thread_id: str, x_user: Optional[str] = Header(None, convert_underscores=True)):
    if not x_user: raise HTTPException(401, "missing X-User")
    with conn() as c, c.cursor() as cur:
        cur.execute("""
        select m.id, u.username as sender, m.subject, m.body, m.created_at
        from smartmail_message m
        join users u on u.id = m.sender_id
        where m.thread_id = %s
        order by m.created_at asc;
        """, (uuid.UUID(thread_id),))
        rows = cur.fetchall()
        return [{"message_id": str(r[0]), "from": r[1], "subject": r[2],
                 "body": r[3], "created_at": r[4].isoformat()+"Z"} for r in rows]

@app.get("/v1/smartmail/search_users")
def search_users(q: str = Query(..., min_length=2), limit: int = 20, offset: int = 0):
    """Search by username OR profile text (topics/tags/location) using FTS."""
    with conn() as c, c.cursor() as cur:
        cur.execute("""
        select u.username, coalesce(p.location,''), coalesce(array_to_string(p.tags, ', '),'')
        from users u
        left join user_profile p on p.user_id = u.id
        where u.username ilike %s
           or (p.search_tsv @@ plainto_tsquery('english', %s))
        order by u.username asc
        limit %s offset %s;
        """, (f"%{q}%", q, limit, offset))
        rows = cur.fetchall()
        return [{"username": r[0], "location": r[1], "tags": r[2]} for r in rows]

# External email via Resend (outbound only)
import requests
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

@app.post("/v1/smartmail/send_external")
def send_external(payload: SendExternalBody, x_user: Optional[str] = Header(None, convert_underscores=True)):
    if not RESEND_API_KEY:
        raise HTTPException(500, "RESEND_API_KEY not set")
    if not x_user: raise HTTPException(401, "missing X-User (used as sender name)")
    from_email = os.getenv("RESEND_FROM", "noreply@mail.smartnet.app")
    data = {
        "from": f"{x_user} <{from_email}>",
        "to": payload.to_emails,
        "subject": payload.subject,
        "html": payload.body_html
    }
    r = requests.post("https://api.resend.com/emails", json=data,
                      headers={"Authorization": f"Bearer {RESEND_API_KEY}",
                               "Content-Type": "application/json"})
    if r.status_code >= 300:
        raise HTTPException(r.status_code, r.text)
    return {"ok": True, "resend": r.json()}
