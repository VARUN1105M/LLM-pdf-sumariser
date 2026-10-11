import datetime
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), default="New Growth Conversation")
    provider: Mapped[str] = mapped_column(String(50), default="ollama")
    model_name: Mapped[str] = mapped_column(String(100), default="mistral")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        default=datetime.datetime.utcnow, 
        onupdate=datetime.datetime.utcnow
    )

    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", 
        back_populates="session", 
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    artifacts: Mapped[List["Artifact"]] = relationship(
        "Artifact", 
        back_populates="session", 
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "provider": self.provider,
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": len(self.messages) if self.messages else 0
        }

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20)) # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    artifacts: Mapped[List["Artifact"]] = relationship("Artifact", back_populates="message", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "citations": self.citations or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "artifacts": [a.to_dict() for a in self.artifacts] if self.artifacts else []
        }

class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    message_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    artifact_type: Mapped[str] = mapped_column(String(50)) # 'markdown', 'html'
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="artifacts")
    message: Mapped[Optional["ChatMessage"]] = relationship("ChatMessage", back_populates="artifacts")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "title": self.title,
            "artifact_type": self.artifact_type,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
