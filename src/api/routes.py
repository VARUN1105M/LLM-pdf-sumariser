import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.config import settings
from src.database.session import get_db_session
from src.database.models import ChatSession, ChatMessage, Artifact
from src.knowledge.ingestion import KnowledgeBase
from src.knowledge.retriever import LennyRetriever
from src.agent.core import LennyGrowthAgent
from src.api.schemas import (
    HealthResponse,
    ModelConfigResponse,
    ModelConfigRequest,
    CreateSessionRequest,
    SessionSummaryResponse,
    SessionDetailResponse,
    ChatQueryRequest,
    ChatQueryResponse,
    MessageSchema,
    CitationSchema,
    ArtifactSchema
)

logger = logging.getLogger("lenny_assistant.routes")
router = APIRouter()

# Singletons initialized in server lifespan
kb = KnowledgeBase()
retriever = LennyRetriever(kb)
agent = LennyGrowthAgent(retriever)

current_model_config = {
    "provider": settings.DEFAULT_LLM_PROVIDER,
    "model_name": settings.OLLAMA_MODEL
}

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check and diagnostic status."""
    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        database="connected",
        indexed_chunks=len(kb.chunks),
        default_provider=current_model_config["provider"]
    )

@router.get("/models", response_model=ModelConfigResponse)
async def get_models():
    """Retrieve active and supported LLM providers."""
    return ModelConfigResponse(
        provider=current_model_config["provider"],
        model_name=current_model_config["model_name"],
        available_providers=["ollama", "anthropic", "openai"],
        ollama_url=settings.OLLAMA_BASE_URL
    )

@router.post("/models", response_model=ModelConfigResponse)
async def set_models(req: ModelConfigRequest):
    """Dynamically toggle the underlying LLM provider."""
    provider = req.provider.lower().strip()
    if provider not in ["ollama", "anthropic", "openai"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Provider must be one of: 'ollama', 'anthropic', 'openai'"
        )

    current_model_config["provider"] = provider
    if req.model_name:
        current_model_config["model_name"] = req.model_name
    else:
        if provider == "ollama":
            current_model_config["model_name"] = settings.OLLAMA_MODEL
        elif provider == "anthropic":
            current_model_config["model_name"] = settings.ANTHROPIC_MODEL
        elif provider == "openai":
            current_model_config["model_name"] = settings.OPENAI_MODEL

    return ModelConfigResponse(
        provider=current_model_config["provider"],
        model_name=current_model_config["model_name"],
        available_providers=["ollama", "anthropic", "openai"],
        ollama_url=settings.OLLAMA_BASE_URL
    )

@router.get("/sessions", response_model=List[SessionSummaryResponse])
async def list_sessions(db: AsyncSession = Depends(get_db_session)):
    """List all user conversation sessions."""
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    
    summaries = []
    for s in sessions:
        # Load count of messages
        msg_res = await db.execute(select(ChatMessage).where(ChatMessage.session_id == s.id))
        count = len(msg_res.scalars().all())
        summaries.append(SessionSummaryResponse(
            id=s.id,
            title=s.title,
            provider=s.provider,
            model_name=s.model_name,
            created_at=s.created_at.isoformat() if s.created_at else None,
            updated_at=s.updated_at.isoformat() if s.updated_at else None,
            message_count=count
        ))
    return summaries

@router.post("/sessions", response_model=SessionSummaryResponse)
async def create_session(req: CreateSessionRequest, db: AsyncSession = Depends(get_db_session)):
    """Start a new chat session."""
    session = ChatSession(
        id=str(uuid.uuid4()),
        title=req.title or "New Growth Chat",
        provider=req.provider or current_model_config["provider"],
        model_name=req.model_name or current_model_config["model_name"]
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionSummaryResponse(
        id=session.id,
        title=session.title,
        provider=session.provider,
        model_name=session.model_name,
        created_at=session.created_at.isoformat() if session.created_at else None,
        updated_at=session.updated_at.isoformat() if session.updated_at else None,
        message_count=0
    )

@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db_session)):
    """Get full session history and message timeline."""
    sess_res = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = sess_res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_res = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
    )
    messages = msg_res.scalars().all()

    # Load artifacts for each message
    formatted_msgs = []
    for m in messages:
        art_res = await db.execute(select(Artifact).where(Artifact.message_id == m.id))
        arts = [a.to_dict() for a in art_res.scalars().all()]
        formatted_msgs.append(MessageSchema(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            citations=m.citations or [],
            artifacts=arts,
            created_at=m.created_at.isoformat() if m.created_at else None
        ))

    return SessionDetailResponse(
        session=SessionSummaryResponse(
            id=session.id,
            title=session.title,
            provider=session.provider,
            model_name=session.model_name,
            created_at=session.created_at.isoformat() if session.created_at else None,
            updated_at=session.updated_at.isoformat() if session.updated_at else None,
            message_count=len(messages)
        ),
        messages=formatted_msgs
    )

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db_session)):
    """Delete a conversation session."""
    await db.execute(delete(ChatSession).where(ChatSession.id == session_id))
    await db.commit()
    return {"status": "deleted", "session_id": session_id}

@router.post("/chat", response_model=ChatQueryResponse)
async def chat_endpoint(req: ChatQueryRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Main conversational agent endpoint:
    - Preserves session context
    - Performs transcript grounding and citations
    - Invokes skills (Ship 30 for 30, Claude-style Artifact generation)
    - Persists interaction to database
    """
    session_id = req.session_id
    session = None

    if session_id:
        sess_res = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = sess_res.scalar_one_or_none()

    if not session:
        # Create fresh session if not specified or not found
        session_id = str(uuid.uuid4())
        # Generate initial title from query snippet
        clean_title = req.query.strip().split("\n")[0][:40] + ("..." if len(req.query) > 40 else "")
        session = ChatSession(
            id=session_id,
            title=clean_title or "New Growth Chat",
            provider=req.provider or current_model_config["provider"],
            model_name=req.model_name or current_model_config["model_name"]
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 1. Fetch previous session history
    history_res = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
    )
    past_messages = history_res.scalars().all()
    history_payload = [{"role": m.role, "content": m.content} for m in past_messages]

    # 2. Record User message
    user_msg_id = str(uuid.uuid4())
    user_msg = ChatMessage(
        id=user_msg_id,
        session_id=session_id,
        role="user",
        content=req.query
    )
    db.add(user_msg)
    await db.commit()

    # 3. Execute Lenny Growth Agent
    provider_to_use = req.provider or session.provider or current_model_config["provider"]
    model_to_use = req.model_name or session.model_name or current_model_config["model_name"]

    try:
        agent_result = await agent.execute(
            query=req.query,
            session_history=history_payload,
            provider_name=provider_to_use,
            model_name=model_to_use
        )
    except Exception as e:
        logger.error(f"Agent execution failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # 4. Record Assistant message
    assistant_msg_id = str(uuid.uuid4())
    assistant_msg = ChatMessage(
        id=assistant_msg_id,
        session_id=session_id,
        role="assistant",
        content=agent_result["answer"],
        citations=agent_result["citations"]
    )
    db.add(assistant_msg)

    # 5. Record any generated artifacts
    saved_artifacts = []
    for art in agent_result["artifacts"]:
        artifact_id = str(uuid.uuid4())
        art_model = Artifact(
            id=artifact_id,
            session_id=session_id,
            message_id=assistant_msg_id,
            title=art["title"],
            artifact_type=art["type"],
            content=art["content"]
        )
        db.add(art_model)
        saved_artifacts.append(ArtifactSchema(
            identifier=art["identifier"],
            type=art["type"],
            title=art["title"],
            content=art["content"]
        ))

    await db.commit()

    return ChatQueryResponse(
        session_id=session_id,
        message_id=assistant_msg_id,
        answer=agent_result["answer"],
        citations=[CitationSchema(**c) for c in agent_result["citations"]],
        artifacts=saved_artifacts,
        provider=agent_result["provider"],
        model=agent_result["model"],
        is_ship30=agent_result["is_ship30"]
    )
