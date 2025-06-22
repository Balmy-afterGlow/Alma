import uuid

from sqlmodel import JSON, Field, SQLModel, Text


class Agent(SQLModel, table=True):
    agent_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    instruction: str = Field(sa_type=Text)
    team: list[str] | None = Field(default=None, sa_type=JSON)
    is_system_agent: bool = False
    status: str = Field(default="active")  # Literal["active", "disabled"]

    model_id: uuid.UUID | None = Field(default=None, foreign_key="model.model_id")
    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.user_id", ondelete="CASCADE"
    )
