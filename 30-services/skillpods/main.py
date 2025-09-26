from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os, uuid, json, re, time
from pathlib import Path

from core.models import (
    PodInfo, QueryRequest, Answer, EvalResult, Proposal, LedgerReceipt, NewPodRequest
)
from core.rag import RAGStore
from core.evals import EvalHarness
from core.objective_board import ObjectiveBoard
from core.metrics import Metrics

APP_ROOT = Path(__file__).parent
DATA_ROOT = APP_ROOT / "data"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SmartNET SkillPods", version="1.1.0")

rag = RAGStore(DATA_ROOT / "corpora")
evals = EvalHarness(DATA_ROOT / "evals")
board = ObjectiveBoard(APP_ROOT / "docs" / "constitution.yaml")
metrics = Metrics(DATA_ROOT)

def _pods_dir() -> Path:
    p = DATA_ROOT / "pods"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _pod_path(pod_id: str) -> Path:
    return _pods_dir() / pod_id

@app.get("/pods", response_model=List[PodInfo])
def list_pods():
    items = []
    for d in _pods_dir().glob("*"):
        if d.is_dir():
            meta = d / "meta.json"
            if meta.exists():
                items.append(PodInfo(**json.loads(meta.read_text(encoding="utf-8"))))
    return items

@app.post("/pods", response_model=PodInfo)
def create_pod(req: NewPodRequest):
    pod_id = req.pod_id or str(uuid.uuid4())[:8]
    p = _pod_path(pod_id)
    if p.exists():
        raise HTTPException(400, "pod_id already exists")
    p.mkdir(parents=True, exist_ok=True)
    meta = {
        "pod_id": pod_id,
        "domain": req.domain,
        "owner": req.owner or "system",
        "created_at": int(time.time()),
        "score_gate": req.score_gate or 95,
    }
    (p / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (p / "corpus").mkdir(parents=True, exist_ok=True)
    (p / "evals").mkdir(parents=True, exist_ok=True)
    return PodInfo(**meta)

@app.post("/pods/{pod_id}/ingest")
async def ingest(pod_id: str, 
                 text: Optional[str] = Form(default=None),
                 files: List[UploadFile] = File(default=[])):
    p = _pod_path(pod_id)
    if not p.exists():
        raise HTTPException(404, "pod not found")
    corpus_dir = p / "corpus"
    saved = []
    if text:
        fpath = corpus_dir / f"snippet-{uuid.uuid4().hex[:6]}.md"
        fpath.write_text(text, encoding="utf-8")
        saved.append(fpath.name)
    for up in files:
        content = await up.read()
        name = re.sub(r"[^a-zA-Z0-9_.-]", "_", up.filename)
        fpath = corpus_dir / name
        fpath.write_bytes(content)
        saved.append(name)
    rag.index_pod(pod_id, corpus_dir)
    return {"pod_id": pod_id, "saved": saved}

@app.post("/pods/{pod_id}/query", response_model=Answer)
def query(pod_id: str, req: QueryRequest):
    p = _pod_path(pod_id)
    if not p.exists():
        raise HTTPException(404, "pod not found")
    hits = rag.search(pod_id, req.question, k=req.k or 5)
    context = "\n\n".join([f"[{h['doc_id']}] {h['snippet']}" for h in hits])
    final = (
        f"Draft answer (program-not-train skeleton):\n\n"
        f"Question: {req.question}\n\n"
        f"Context summary from corpus:\n{context}\n\n"
        f"Answer: Based on the retrieved materials, here are the key points...\n"
        f"(Replace this with a true LLM call; this skeleton is RAG-first.)"
    )
    citations = [{"doc_id": h["doc_id"], "score": h["score"]} for h in hits]
    rubik = {
        "child": "Simple, friendly version goes here.",
        "grandma": "Plain-language version with examples.",
        "supporter": "Benefits and quick wins.",
        "tech": "APIs, schemas, step-by-steps.",
        "investor": "Market framing, KPIs, ROI."
    }
    return Answer(pod_id=pod_id, answer=final, citations=citations, rubik=rubik)

@app.post("/pods/{pod_id}/evals/run", response_model=EvalResult)
def run_evals(pod_id: str):
    p = _pod_path(pod_id)
    if not p.exists():
        raise HTTPException(404, "pod not found")
    score = evals.run_suite(pod_id, p / "evals")
    meta_path = p / "meta.json"
    gate = 95
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        gate = int(meta.get("score_gate", 95))
    passed = score >= gate
    receipt = {
        "id": str(uuid.uuid4())[:8],
        "event": "evals.run",
        "pod_id": pod_id,
        "score": score,
        "gate": gate,
        "passed": passed,
        "ts": int(time.time())
    }
    led = DATA_ROOT / "ledger"
    led.mkdir(parents=True, exist_ok=True)
    (led / f"{receipt['id']}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return EvalResult(score=score, gate=gate, passed=passed, receipt_id=receipt["id"])

@app.post("/objective/proposals", response_model=LedgerReceipt)
def propose(proposal: Proposal):
    ok, notes = board.validate(proposal.dict())
    rid = str(uuid.uuid4())[:8]
    payload = {
        "id": rid,
        "event": "objective.proposed",
        "ok": ok,
        "notes": notes,
        "proposal": proposal.dict(),
        "ts": int(time.time())
    }
    led = DATA_ROOT / "ledger"
    led.mkdir(parents=True, exist_ok=True)
    (led / f"{rid}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return LedgerReceipt(**payload)

@app.get("/ledger/receipts/{rid}")
def get_receipt(rid: str):
    path = DATA_ROOT / "ledger" / f"{rid}.json"
    if not path.exists():
        raise HTTPException(404, "not found")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))

# ---------- NEW: SIS metrics ----------
@app.get("/metrics/sis")
def metrics_sis():
    return JSONResponse(metrics.global_summary())

@app.get("/pods/{pod_id}/metrics")
def metrics_pod(pod_id: str):
    data = metrics.global_summary()
    for p in data.get("pods", []):
        if p.get("pod_id") == pod_id:
            return JSONResponse(p)
    raise HTTPException(404, "pod not found")
