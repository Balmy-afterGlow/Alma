"""
聊天相关的Schema定义
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessagePublic(BaseModel):
    """聊天消息的公开展示模型"""

    message_id: uuid.UUID
    role: str
    content: str
    timestamp: datetime
    agent_id: uuid.UUID
    agent_name: str | None = None
    model_metadata: dict | None = None


class ConversationWithMessages(BaseModel):
    """包含消息的对话模型"""

    conversation_id: uuid.UUID
    title: str
    created_at: datetime
    messages: list[ChatMessagePublic]
    messages_count: int


class AgentWithTools(BaseModel):
    """包含工具信息的Agent模型"""

    agent_id: uuid.UUID
    name: str
    instruction: str
    team: list[str] | None = None
    is_system_agent: bool
    status: str
    tools: list[dict] | None = None
    tools_count: int = 0


class UserDashboard(BaseModel):
    """用户仪表板数据模型"""

    llm_configs_count: int
    conversations_count: int
    recent_conversations: list[dict]
    available_agents: list[dict]
