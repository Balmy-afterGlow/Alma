import uuid
from datetime import datetime, timezone
from typing import Any

from sqlmodel import JSON, Field, SQLModel, Text


class Message(SQLModel, table=True):
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    role: str  # Literal["user", "assistant", "system", "tool"]
    content: str = Field(sa_type=Text)
    model_metadata: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = False

    conversation_id: uuid.UUID = Field(
        foreign_key="conversation.conversation_id", index=True, ondelete="CASCADE"
    )
    agent_id: uuid.UUID = Field(foreign_key="agent.agent_id")
