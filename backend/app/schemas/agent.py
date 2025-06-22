import uuid

from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    name: str = Field(max_length=100)
    instruction: str
    team: list[str] | None = None
    is_system_agent: bool = False
    status: str = Field(default="active")  # "active" or "disabled"


class AgentCreate(AgentBase):
    model_id: uuid.UUID | None = None


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    instruction: str | None = None
    team: list[str] | None = None
    status: str | None = None
    model_id: uuid.UUID | None = None


class AgentPublic(AgentBase):
    agent_id: uuid.UUID
    model_id: uuid.UUID | None
    user_id: uuid.UUID | None


class AgentsPublic(BaseModel):
    data: list[AgentPublic]
    count: int
