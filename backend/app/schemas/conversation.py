import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConversationBase(BaseModel):
    title: str = Field(default="New Chat", max_length=200)


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class ConversationPublic(ConversationBase):
    conversation_id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID


class ConversationsPublic(BaseModel):
    data: list[ConversationPublic]
    count: int
