from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    database: str
    indexed_chunks: int
    default_provider: str

class ModelConfigRequest(BaseModel):
    provider: str = Field(..., description="'ollama', 'anthropic', or 'openai'")
    model_name: Optional[str] = Field(None, description="Specific model tag or name")

class ModelConfigResponse(BaseModel):
    provider: str
    model_name: str
    available_providers: List[str]
    ollama_url: str

class CreateSessionRequest(BaseModel):
    title: Optional[str] = Field("New Growth Chat", description="Initial session title")
    provider: Optional[str] = Field(None, description="Preferred provider for session")
    model_name: Optional[str] = Field(None, description="Preferred model")

class SessionSummaryResponse(BaseModel):
    id: str
    title: str
    provider: str
    model_name: str
    created_at: Optional[str]
    updated_at: Optional[str]
    message_count: int

class CitationSchema(BaseModel):
    source_index: int
    chunk_id: str
    guest: str
    guest_role: Optional[str] = ""
    title: str
    episode: Optional[str] = ""
    timestamp: Optional[str] = ""
    url: Optional[str] = ""
    snippet: str

class ArtifactSchema(BaseModel):
    identifier: str
    type: str # 'markdown' or 'html'
    title: str
    content: str

class MessageSchema(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: List[CitationSchema] = []
    artifacts: List[Dict[str, Any]] = []
    created_at: Optional[str] = None

class SessionDetailResponse(BaseModel):
    session: SessionSummaryResponse
    messages: List[MessageSchema]

class ChatQueryRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Existing session ID or null to create new")
    query: str = Field(..., min_length=1, description="User prompt or question")
    provider: Optional[str] = Field(None, description="Override LLM provider")
    model_name: Optional[str] = Field(None, description="Override LLM model")

class ChatQueryResponse(BaseModel):
    session_id: str
    message_id: str
    answer: str
    citations: List[CitationSchema]
    artifacts: List[ArtifactSchema]
    provider: str
    model: str
    is_ship30: bool
