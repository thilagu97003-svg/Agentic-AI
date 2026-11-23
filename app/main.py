import json
import markdown
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import Base, engine, get_db
from app.db import models  # noqa: registers tables
from app.db.models import Incident, Message, ActionLog, Report
from app.agent.graph import run_turn
from app.agent.nodes import is_feedback
from app.services.redis_state import load_session
from app.services.report import build_report
from app.config import settings
from app.llm import provider_chain, STATE, describe_image

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Autonomous IT Helpdesk & Incident Resolution Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str
    attachment_text: str = ""   # text read from an uploaded file or screenshot
    attachment_name: str = ""


class ChatResponse(BaseModel):
    reply: str
    incident_id: int
    category: str | None = None
    priority: str | None = None
    status: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    session = load_session(req.session_id)
    feedback_turn = is_feedback(session.get("status"), req.message)

    result = run_turn(req.session_id, req.message, req.attachment_text)
    if result.get("ack_only"):  # reply after the incident is closed, no new incident
        last = (
            db.query(Incident)
            .filter(Incident.session_id == req.session_id)
            .order_by(Incident.id.desc())
            .first()
        )
        if last:
            return ChatResponse(
                reply=result["answer"],
                incident_id=last.id,
                category=last.category,
                priority=last.priority,
                status=last.status,
            )

    inc = None
    if feedback_turn:  # reply to "Did this resolve your issue?"
        inc = (
            db.query(Incident)
            .filter(Incident.session_id == req.session_id, Incident.status == "open")
            .order_by(Incident.id.desc())
            .first()
        )
    if inc is None:  # new issue = new incident
        inc = Incident(
            session_id=req.session_id,
            title=req.message[:250],
            category=result.get("category"),
            priority=result.get("priority"),
            status="open",
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)

    user_text = req.message + (f"\n(Attached: {req.attachment_name})" if req.attachment_name else "")
    db.add(Message(incident_id=inc.id, role="user", content=user_text))
    db.add(Message(incident_id=inc.id, role="assistant", content=result["answer"]))
    for a in result.get("action_log", []):
        db.add(ActionLog(
            incident_id=inc.id,
            tool_name=a["tool"],
            tool_input=json.dumps(a["input"]),
            tool_output=a["output"],
        ))

    status = result.get("status", "open")
    inc.status = "open" if status in ("new", "awaiting_feedback") else status
    if status == "resolved":
        inc.resolution = result.get("resolution")
    db.commit()

    if inc.status in ("resolved", "escalated"):  # auto incident report
        content = build_report(db, inc)
        rep = db.query(Report).filter(Report.incident_id == inc.id).first()
        if rep:
            rep.content = content
        else:
            db.add(Report(incident_id=inc.id, content=content))
        db.commit()

    return ChatResponse(
        reply=result["answer"],
        incident_id=inc.id,
        category=inc.category,
        priority=inc.priority,
        status=inc.status,
    )


IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
TEXT_TYPES = {".txt", ".log", ".csv", ".json", ".md"}


@app.post("/api/upload")
def upload(file: UploadFile = File(...)):
    """Read a screenshot (vision model) or a text/log file and return text for the agent."""
    name = file.filename or "file"
    ext = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
    if ext not in IMAGE_TYPES and ext not in TEXT_TYPES:
        raise HTTPException(400, "Allowed files: png, jpg, webp, txt, log, csv, json, md")

    limit = settings.MAX_UPLOAD_MB * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"File too large (max {settings.MAX_UPLOAD_MB} MB)")

    if ext in IMAGE_TYPES:
        text = describe_image(data, IMAGE_TYPES[ext])
        if not text:
            raise HTTPException(
                422, "Could not read this image (no vision model available). Please describe the problem in text."
            )
        return {"name": name, "kind": "image", "text": text[:2000]}

    text = data.decode("utf-8", errors="ignore").strip()
    return {"name": name, "kind": "text", "text": text[:3000]}


@app.get("/api/incidents")
def list_incidents(db: Session = Depends(get_db)):
    rows = db.query(Incident).order_by(Incident.id.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "priority": r.priority,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@app.get("/api/report/{incident_id}", response_class=PlainTextResponse)
def get_report(incident_id: int, db: Session = Depends(get_db)):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    rep = db.query(Report).filter(Report.incident_id == incident_id).first()
    return rep.content if rep else build_report(db, inc)

@app.get("/api/report/{incident_id}/view", response_class=HTMLResponse)
def view_report(incident_id: int, db: Session = Depends(get_db)):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    rep = db.query(Report).filter(Report.incident_id == incident_id).first()
    text = rep.content if rep else build_report(db, inc)
    body = markdown.markdown(text)
    return f"""<html><head><title>Incident Report #{incident_id}</title>
    <style>
      body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 30px auto; line-height: 1.6; color: #222; }}
      h1 {{ border-bottom: 2px solid #2563eb; padding-bottom: 6px; }}
      h2 {{ color: #2563eb; margin-top: 24px; }}
      code {{ background: #f3f4f6; padding: 2px 5px; border-radius: 4px; }}
    </style></head><body>{body}</body></html>"""
@app.get("/api/info")
def info():
    return {
        "provider_order": provider_chain(),
        "last_used": STATE["last_provider"],
        "embeddings": settings.EMBED_MODEL,
    }