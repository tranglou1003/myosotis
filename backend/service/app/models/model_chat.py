from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.model_base import BareBaseModel

class ChatSession(BareBaseModel):
    __tablename__ = "chat_sessions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_number = Column(Integer, nullable=False)  # số session riêng cho từng user
    session_name = Column(String, default="Chat Session")
    last_active_at = Column(DateTime, default=func.now())
    total_messages = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "session_number", name="uq_user_session_number"),
    )


class ChatMessage(BareBaseModel):
    __tablename__ = "chat_messages"

    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    session = relationship("ChatSession", back_populates="messages")
