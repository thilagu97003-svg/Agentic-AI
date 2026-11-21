from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent import nodes as n
from app.services.redis_state import load_session, save_session


def route_entry(state):
    return "feedback_node" if state.get("status") == "awaiting_feedback" else "classify_node"


def route_after_classify(state):
    if state["priority"] == "critical" or state["category"] == "security":
        return "escalate_node"
    return "action_node" if state.get("action") else "retrieve_node"


def route_after_grade(state):
    if state["relevant"]:
        return "generate_node"
    return "rewrite_node" if state.get("retries", 0) < 1 else "escalate_node"


def route_after_feedback(state):
    return {"yes": "resolve_node", "no": "escalate_node"}.get(state["feedback"], END)


# node names end with _node, so they never clash with state keys
g = StateGraph(AgentState)
g.add_node("classify_node", n.classify_node)
g.add_node("action_node", n.action_node)
g.add_node("retrieve_node", n.retrieve_node)
g.add_node("grade_node", n.grade_node)
g.add_node("rewrite_node", n.rewrite_node)
g.add_node("generate_node", n.generate_node)
g.add_node("feedback_node", n.feedback_node)
g.add_node("resolve_node", n.resolve_node)
g.add_node("escalate_node", n.escalate_node)

g.add_conditional_edges(START, route_entry, ["classify_node", "feedback_node"])
g.add_conditional_edges("classify_node", route_after_classify, ["escalate_node", "action_node", "retrieve_node"])
g.add_edge("action_node", "retrieve_node")
g.add_edge("retrieve_node", "grade_node")
g.add_conditional_edges("grade_node", route_after_grade, ["generate_node", "rewrite_node", "escalate_node"])
g.add_edge("rewrite_node", "retrieve_node")
g.add_edge("generate_node", END)
g.add_conditional_edges("feedback_node", route_after_feedback, ["resolve_node", "escalate_node", END])
g.add_edge("resolve_node", END)
g.add_edge("escalate_node", END)

graph = g.compile()

SAVE_KEYS = ["issue", "category", "priority", "status", "last_answer", "sources"]


def run_turn(session_id: str, message: str) -> dict:
    session = load_session(session_id)
    if session.get("status") in ("resolved", "escalated") and n.is_ack(message):
        return {
            "answer": f"This incident is already {session['status']}. Please describe a new issue and I will open a new incident.",
            "status": session["status"],
            "ack_only": True,
        }
    if n.is_feedback(session.get("status"), message):
        state_in = {**session, "message": message, "action_log": []}
    else:  # new incident
        state_in = {
            "session_id": session_id, "message": message, "issue": message,
            "query": message, "retries": 0, "status": "new", "docs": [], "action_log": [],
        }
    result = graph.invoke(state_in)
    save_session(session_id, {k: result.get(k) for k in SAVE_KEYS})  # Redis state
    return result