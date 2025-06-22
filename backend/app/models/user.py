import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from pydantic import EmailStr
from sqlmodel import JSON, Field, SQLModel

from app.utils.nickname import generate_default_nickname


class User(SQLModel, table=True):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nickname: str = Field(default_factory=generate_default_nickname, max_length=50)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_superuser: bool = False
    is_active: bool = False
    timezone: str = Field(default="UTC+8:00", max_length=50)
    language: str = Field(default="zh", max_length=10)
    preferences: dict[str, Any] | None = Field(default=None, sa_type=JSON)
