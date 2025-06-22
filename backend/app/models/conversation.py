import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(default="New Chat")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_id: uuid.UUID = Field(
        foreign_key="user.user_id", index=True, ondelete="CASCADE"
    )
