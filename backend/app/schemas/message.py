import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    role: str = Field(pattern="^(user|assistant|system|tool)$")
    content: str
    model_metadata: dict[str, Any] | None = None


class MessageCreate(MessageBase):
    conversation_id: uuid.UUID
    agent_id: uuid.UUID


class MessageUpdate(BaseModel):
    content: str | None = None
    model_metadata: dict[str, Any] | None = None
    is_deleted: bool | None = None


class MessagePublic(MessageBase):
    message_id: uuid.UUID
    timestamp: datetime
    is_deleted: bool
    conversation_id: uuid.UUID
    agent_id: uuid.UUID


class MessagesPublic(BaseModel):
    data: list[MessagePublic]
    count: int
