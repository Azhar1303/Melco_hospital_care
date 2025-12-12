from typing import Optional, List, Dict
from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    role: str = "patient"
    message: str
    session_id: Optional[str] = None


class OrchestratorResponse(BaseModel):
    session_id: str
    message: str
    next_action: str  # "ask_more_info", "completed", "out_of_scope", "error"
    selected_agent: Optional[str] = None
    data: Optional[Dict] = None
    missing_fields: Optional[List[str]] = None
