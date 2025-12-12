# models/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class OrchestratorResponse(BaseModel):
    session_id: str
    message: str
    next_action: str
    selected_agent: Optional[str] = None
    data: Optional[Dict[str, Any]] = None  # ✅ THIS FIXES YOUR ERRORS PERMANENTLY
