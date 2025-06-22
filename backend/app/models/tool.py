import uuid
from typing import Any

from sqlmodel import JSON, Field, SQLModel, Text


class Tool(SQLModel, table=True):
    tool_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True)
    parameters: dict[str, Any] = Field(sa_type=JSON)
    description: str | None = Field(default=None, sa_type=Text)
    implementation: str | None = Field(default=None, sa_type=Text)
