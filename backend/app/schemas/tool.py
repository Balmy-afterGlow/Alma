import uuid
from typing import Any

from pydantic import BaseModel, Field


class ToolBase(BaseModel):
    name: str = Field(max_length=100)
    parameters: dict[str, Any]
    description: str | None = None
    implementation: str | None = None


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    parameters: dict[str, Any] | None = None
    description: str | None = None
    implementation: str | None = None


class ToolPublic(ToolBase):
    tool_id: uuid.UUID


class ToolsPublic(BaseModel):
    data: list[ToolPublic]
    count: int
