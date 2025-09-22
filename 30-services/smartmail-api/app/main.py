# repo: smartnet-pod-golden
# path: 30-services/smartmail-api/app/main.py
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import os, uuid, datetime
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/smartnet")

app = FastAPI(title="SmartMail API (mini)", version="0.1.0")

def conn():
    return psycopg.connect(DATABASE_URL, autocommit=True)

class SendInternalBody(BaseModel):
    to_usernames: List[str] = Field(..., min_items=1)
    subject: str = Field("", max_length=255)
    body: str = Field(..., max_length=20000)

@app.get("/health")
def health():
    with conn() as c:
        with c.cursor() as cur:
            cur.execute("select 1;")
            return {"ok": True}

def _get_user_id(cur, username: str):
    cur.execute("select id from users where username=%s;", (username,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, f"user not found: {username}")
    return row[0]

@app.post("/v1/smartmail/send_internal")
def send_internal(payload: SendInternalBody, x_user: Optional[str] = Header(None, convert_underscores=True)):
    if not x_user:
        raise HTTPException(401, "missing X-User header (sender username)")
    with conn() as c, c.cursor() as cur:
        sender_id = _get_user_id(cur, x_user)
        now = datetime.datetime.utcnow()
        # save one row per recipient + one sender copy
        for uname in payload.to_usernames:
            rid = _get_user_id(cur, uname)
            mid = uuid.uuid4()
            cur.execute("""
              insert into smartmail_message(id, sender_id, recipient_id, subject, body, created_at)
              values (%s,%s,%s,%s,%s,%s);
            """, (mid, sender_id, rid, payload.subject, payload.body, now))
        # sender copy
        mid = uuid.uuid4()
        cur.execute("""
          insert into smartmail_message(id, sender_id, recipient_id, subject, body, created_at, sender_copy)
          values (%s,%s,%s,%s,%s,%s,true);
        """, (mid, sender_id, sender_id, payload.subject, payload.body, now))
        return {"ok": True}

@app.get("/v1/smartmail/mailbox")
def mailbox(folder: str = Query("inbox", pattern="^(inbox|sent)$"),
            limit: int = 20, offset: int = 0,
            x_user: Optional[str] = Header(None, convert_underscores=True)):
    if not x_user:
        raise HTTPException(401, "missing X-User")
    with conn() as c, c.cursor() as cur:
        uid = _get_user_id(cur, x_user)
        if folder == "inbox":
            cur.execute("""
              select m.id, u.username as sender, m.subject, left(m.body,280) as snippet, m.created_at
              from smartmail_message m
              join users u on u.id = m.sender_id
              where m.recipient_id=%s and m.sender_copy=false
              order by m.created_at desc
              limit %s offset %s;
            """, (uid, limit, offset))
        else:
            cur.execute("""
              select m.id, u.username as recipient, m.subject, left(m.body,280) as snippet, m.created_at
              from smartmail_message m
              join users u on u.id = m.recipient_id
              where m.sender_id=%s and m.sender_copy=true
              order by m.created_at desc
              limit %s offset %s;
            """, (uid, limit, offset))
        rows = cur.fetchall()
        return [{"message_id": str(r[0]), "peer": r[1], "subject": r[2],
                 "snippet": r[3], "created_at": r[4].isoformat()+"Z"} for r in rows]
