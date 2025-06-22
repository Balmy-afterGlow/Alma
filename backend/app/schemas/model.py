import uuid

from pydantic import BaseModel, Field


class ModelBase(BaseModel):
    name: str = Field(max_length=100)
    base_url: str | None = None


class ModelCreate(ModelBase):
    llm_id: uuid.UUID


class ModelUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    base_url: str | None = None


class ModelPublic(ModelBase):
    model_id: uuid.UUID
    llm_id: uuid.UUID


class ModelsPublic(BaseModel):
    data: list[ModelPublic]
    count: int
