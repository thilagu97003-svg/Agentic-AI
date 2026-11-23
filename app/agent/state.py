from typing import TypedDict, List, Optional


class AgentState(TypedDict, total=False):
    session_id: str
    message: str
    issue: str
    query: str
    category: str
    priority: str
    action: Optional[str]
    action_args: dict
    action_result: Optional[str]
    action_log: List[dict]
    docs: List[str]
    sources: List[str]
    categories: List[str]
    relevant: bool
    retries: int
    has_attachment: bool
    feedback: str
    answer: str
    last_answer: str
    resolution: str
    status: str  # new / awaiting_feedback / resolved / escalated