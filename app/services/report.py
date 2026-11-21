from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import Incident, Message, ActionLog


def _short(text, n=220):
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[:n] + "..."


def build_report(db: Session, inc: Incident) -> str:
    msgs = db.query(Message).filter(Message.incident_id == inc.id).order_by(Message.id).all()
    acts = db.query(ActionLog).filter(ActionLog.incident_id == inc.id).order_by(ActionLog.id).all()

    outcome = {
        "resolved": "Resolved through guided self-service troubleshooting. User confirmed the fix.",
        "escalated": "Escalated to the L2 support team for human follow-up.",
    }.get(inc.status, "Open, waiting for user feedback.")

    lines = [
        f"# Incident Report #{inc.id}",
        "",
        f"Generated: {datetime.utcnow():%Y-%m-%d %H:%M} UTC",
        "",
        "## Summary",
        f"- **User:** {inc.user_name}",
        f"- **Category:** {inc.category}",
        f"- **Priority:** {inc.priority}",
        f"- **Status:** {inc.status}",
        f"- **Reported at:** {inc.created_at:%Y-%m-%d %H:%M} UTC",
        "",
        "## Issue reported",
        inc.title or "",
        "",
        "## Conversation timeline",
    ]
    for m in msgs:
        who = "User" if m.role == "user" else "Agent"
        lines.append(f"- [{m.created_at:%H:%M:%S}] **{who}:** {_short(m.content)}")

    lines += ["", "## Actions performed"]
    if acts:
        for a in acts:
            lines.append(f"- `{a.tool_name}` input: {a.tool_input} -> {a.tool_output}")
    else:
        lines.append("- No automated actions were run.")

    lines += ["", "## Outcome", outcome]
    if inc.resolution:
        lines += ["", "## Resolution steps provided", inc.resolution]
    return "\n".join(lines)