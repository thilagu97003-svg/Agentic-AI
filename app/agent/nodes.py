import json
import re
from difflib import SequenceMatcher
from langchain_core.documents import Document
from app.config import settings
from app.llm import get_chat_model
from app.rag.retriever import HybridRetriever, grade_documents, rewrite_query
from app.mcp_server import tools
from app.services.redis_state import cache_get, cache_set

llm = get_chat_model()
json_llm = get_chat_model(json_mode=True)

_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


CATEGORIES = ["network", "software", "access", "hardware", "security", "other"]
RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
KEYWORDS = {
    "security": ["phishing", "malware", "virus", "hacked", "ransomware", "suspicious", "breach"],
    "access": ["password", "login", "log in", "locked", "mfa", "otp", "authenticator"],
    "network": ["vpn", "wifi", "wi-fi", "internet", "network"],
    "hardware": ["printer", "laptop", "slow", "blue screen", "bsod", "disk", "keyboard", "battery"],
        "software": ["outlook", "email", "mail", "teams", "zoom", "install", "software", "excel", "word", "office", "app"],
}
HIGH_WORDS = ["urgent", "all users", "everyone", "blue screen", "bsod", "lost phone", "lost my phone", "cannot work"]


def keyword_classify(text: str):
    t = text.lower()
    category = "other"
    for cat in ["security", "access", "network", "hardware", "software"]:
        if any(re.search(r"\b" + re.escape(k), t) for k in KEYWORDS[cat]):
            category = cat
            break
    if category == "security":
        priority = "critical"
    elif any(w in t for w in HIGH_WORDS):
        priority = "high"
    elif category in ("hardware", "software"):
        priority = "low"
    else:
        priority = "medium"
    return category, priority


def detect_action(text: str):
    t = text.lower()
    if "password" in t and any(w in t for w in ["forgot", "reset", "expired"]):
        return "reset_password", {"username": "user"}
    if "locked" in t:
        return "unlock_account", {"username": "user"}
    if "printer" in t and any(w in t for w in ["queue", "stuck", "offline", "not printing"]):
        return "restart_service", {"service": "print_spooler"}
    if "vpn" in t:
        return "check_service_status", {"service": "vpn_gateway"}
    return None, {}


def is_feedback(status, message: str) -> bool:
    """User is answering 'Did this resolve your issue?' (short reply)."""
    return status == "awaiting_feedback" and len(message.split()) <= 6

ACK_RE = re.compile(r"^\s*(yes|no|ok|okay|thanks|thank you|resolved|fixed|nope|still)\b", re.I)


def is_ack(message: str) -> bool:
    """Short 'yes / no / thanks' reply sent after an incident is already closed."""
    return len(message.split()) <= 6 and bool(ACK_RE.match(message))

# ---------------- nodes ----------------

def classify_node(state):
    msg = state["message"]
    category, priority = keyword_classify(msg)
    # long pasted logs or attachment text: keywords are unreliable, let the LLM decide
    # (security keywords are always kept)
    if len(msg.split()) > 80 and category != "security":
        category, priority = "other", "medium"

    if category == "other":  # keywords gave no answer, ask the LLM
        try:
            prompt = (
                "Classify this IT support issue. Reply as JSON with keys "
                '"category" (network, software, access, hardware, security, other) '
                'and "priority" (low, medium, high, critical).\n'
                f"Issue: {msg}"
            )
            data = json.loads(json_llm.invoke(prompt).content)
            c = str(data.get("category", "")).lower()
            p = str(data.get("priority", "")).lower()
            if c in CATEGORIES:
                category = c
            if p in RANK:
                priority = "high" if (p == "critical" and category != "security") else p
        except Exception:
            pass

    if category == "security":
        priority = "critical"

    tool, args = detect_action(msg)
    return {"category": category, "priority": priority, "action": tool, "action_args": args}


def action_node(state):
    result = getattr(tools, state["action"])(**state.get("action_args", {}))
    log = state.get("action_log", []) + [
        {"tool": state["action"], "input": state.get("action_args", {}), "output": result}
    ]
    return {"action_result": result, "action_log": log}


def retrieve_node(state):
    q = state["query"]
    key = "rag:" + q.lower().strip()
    cached = cache_get(key)  # Redis cache
    if cached:
        return cached
    hits = get_retriever().search(q)
    out = {
        "docs": [d.page_content for d in hits],
        "sources": [d.metadata["source"] for d in hits],
        "categories": [d.metadata["category"] for d in hits],
    }
    cache_set(key, out)
    return out


def grade_node(state):
    docs = [Document(page_content=t) for t in state["docs"]]
    ok = grade_documents(state["query"], docs)
    short = len(state["issue"].split()) <= 40  # category shortcut only for short, normal requests
    category_match = short and state.get("category") in state.get("categories", [])[:2]
    return {"relevant": ok or category_match}


def rewrite_node(state):
    return {"query": rewrite_query(state["issue"]), "retries": state.get("retries", 0) + 1}

SKIP_SECTIONS = ("permitted actions", "escalate when")


def usable(text: str) -> bool:
    first_line = text.split("\n", 1)[0].lower()
    return not first_line.endswith(SKIP_SECTIONS)

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def dedupe_steps(text: str) -> str:
    """Drop repeated or near-duplicate numbered steps and renumber."""
    intro, steps = [], []
    for line in text.splitlines():
        m = re.match(r"^\s*\d+[.)]\s*(.+)$", line)
        if m:
            step = m.group(1).strip()
            if any(SequenceMatcher(None, _norm(step), _norm(k)).ratio() >= 0.75 for k in steps):
                continue
            steps.append(step)
        elif not steps and line.strip():
            intro.append(line.strip())
    if not steps:
        return text
    body = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    return ("\n".join(intro) + "\n\n" if intro else "") + body

def generate_node(state):
        top = state["sources"][0] if state.get("sources") else None
        docs = [d for d, s in zip(state["docs"], state["sources"]) if s == top] or state["docs"]
        docs = [d for d in docs if usable(d)] or [d for d in state["docs"] if usable(d)]
        if not docs:
            return {
            "answer": "I could not find a matching article. Please describe the issue in more detail, for example VPN, Wi-Fi, password or printer.",
            "status": "new",
        }
        context = "\n\n".join(docs)
        note = f"\nAction already performed: {state['action_result']}\n" if state.get("action_result") else ""
        prompt = (
        "You are an IT helpdesk assistant. Use ONLY the knowledge base below.\n"
        f"User issue: {state['issue']}\n{note}\n"
        f"Knowledge base:\n{context}\n\n"
               "Reply in a short, friendly way with numbered troubleshooting steps (maximum 6). "
                "Use only steps from the knowledge base. Do not add closing lines and do not ask a question at the end."
    )
        answer = dedupe_steps(llm.invoke(prompt).content.strip())
        return {
        "last_answer": answer,
        "answer": answer + "\n\nDid this resolve your issue? (yes / no)",
        "status": "awaiting_feedback",
    }


def analyze_node(state):
    """No KB article matched, but the user sent a screenshot or log: explain it and suggest safe steps."""
    prompt = (
        "You are an IT helpdesk assistant. The user sent a screenshot description or a log or error text. "
        "No knowledge base article matches it.\n"
        f"User message and attachment details:\n{state['issue'][:3000]}\n\n"
        "If this does not describe an IT problem, reply with exactly: "
        "I could not find an IT problem in this attachment. Please describe the issue in text.\n"
        "Otherwise: first explain in one or two simple sentences what the problem or error means, "
        "then give 3 to 5 short, safe troubleshooting steps as a numbered list. "
        "Never suggest risky actions such as registry edits, deleting system files or disabling security software. "
        "Do not ask a question at the end."
    )
    answer = llm.invoke(prompt).content.strip()
    if answer.startswith("I could not find an IT problem"):
        return {"answer": answer, "status": "new"}
    return {
        "last_answer": answer,
        "answer": (
            "I could not find a matching knowledge base article, so I analyzed your attachment:\n\n"
            + answer
            + "\n\nDid this resolve your issue? (yes / no)"
        ),
        "status": "awaiting_feedback",
    }


def feedback_node(state):
    t = state["message"].lower()
    if re.search(r"\b(no|not|still|nope|didn't|doesn't|failed)\b", t):
        return {"feedback": "no"}
    if re.search(r"\b(yes|resolved|fixed|worked|solved|thanks|thank)\b", t):
        return {"feedback": "yes"}
    return {
        "feedback": "unclear",
        "answer": "Please reply 'yes' if your issue is resolved, or 'no' if it is still not working.",
    }


def resolve_node(state):
    return {
        "status": "resolved",
        "resolution": state.get("last_answer", ""),
        "answer": "Great, glad it is resolved ✅ I have closed this incident and generated the report.",
    }


def escalate_node(state):
    if state.get("priority") == "critical" or state.get("category") == "security":
        reason = "Critical or security incident, needs human review"
    elif state.get("feedback") == "no":
        reason = "Self-service steps did not resolve the issue"
    else:
        reason = "No relevant knowledge base article found"
    result = tools.escalate_incident(reason)
    log = state.get("action_log", []) + [
        {"tool": "escalate_incident", "input": {"reason": reason}, "output": result}
    ]
    return {
        "status": "escalated",
        "action_log": log,
        "answer": (
            f"I have escalated this incident to the L2 support team.\n"
            f"Reason: {reason}\nCategory: {state.get('category')} | Priority: {state.get('priority')}\n"
            "A support engineer will contact you shortly."
        ),
    }