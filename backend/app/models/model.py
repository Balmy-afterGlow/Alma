import uuid

from sqlmodel import Field, SQLModel


class Model(SQLModel, table=True):
    model_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    base_url: str | None = Field(default=None)

    llm_id: uuid.UUID = Field(foreign_key="llmconfig.llm_id", ondelete="CASCADE")
