import uuid

from sqlmodel import Field, SQLModel


class AgentTools(SQLModel, table=True):
    agent_id: uuid.UUID = Field(foreign_key="agent.agent_id", primary_key=True)
    tool_id: uuid.UUID = Field(foreign_key="tool.tool_id", primary_key=True)
