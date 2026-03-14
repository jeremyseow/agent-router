from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from core.constants import IngestionStatus

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

class ChatResponse(BaseModel):
    response: str
    agent_used: Optional[str] = None

class IngestionJobStatus(BaseModel):
    job_id: UUID
    filename: str
    status: IngestionStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class IngestResult(BaseModel):
    document: str
    job_id: Optional[UUID] = None
    status: IngestionStatus

class IngestResponse(BaseModel):
    results: List[IngestResult]
