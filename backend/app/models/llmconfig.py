import uuid

from sqlmodel import Field, SQLModel


class LLMConfig(SQLModel, table=True):
    llm_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    provider: str
    api_key_encrypted: str

    user_id: uuid.UUID = Field(foreign_key="user.user_id", ondelete="CASCADE")
