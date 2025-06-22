import uuid

from pydantic import BaseModel, Field


class LLMConfigBase(BaseModel):
    provider: str = Field(max_length=50)


class LLMConfigCreate(LLMConfigBase):
    api_key: str  # 明文密钥，在保存时会被加密


class LLMConfigUpdate(BaseModel):
    provider: str | None = Field(default=None, max_length=50)
    api_key: str | None = None  # 明文密钥，在保存时会被加密


class LLMConfigPublic(LLMConfigBase):
    llm_id: uuid.UUID
    user_id: uuid.UUID
    # 注意：不返回加密的API密钥


class LLMConfigsPublic(BaseModel):
    data: list[LLMConfigPublic]
    count: int
