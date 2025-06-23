"""
聊天相关的Schema定义
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AgentEventPublic(BaseModel):
    """智能体事件的公开展示模型"""

    event_type: str
    timestamp: str
    agent_name: str
    data: dict[str, Any] | None = None


class ChatMessagePublic(BaseModel):
    """聊天消息的公开展示模型"""

    message_id: uuid.UUID
    role: str
    content: str
    timestamp: datetime
    agent_id: uuid.UUID
    agent_name: str | None = None
    model_metadata: dict | None = None


class ChatMessageWithEvents(ChatMessagePublic):
    """包含事件信息的聊天消息模型"""

    events: list[AgentEventPublic] | None = None
    model_used: str | None = None
    tools_available: int = 0


class ConversationWithMessages(BaseModel):
    """包含消息的对话模型"""

    conversation_id: uuid.UUID
    title: str
    created_at: datetime
    messages: list[ChatMessagePublic]
    messages_count: int


class ConversationWithEventsMessages(BaseModel):
    """包含带事件信息的消息的对话模型"""

    conversation_id: uuid.UUID
    title: str
    created_at: datetime
    messages: list[ChatMessageWithEvents]
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


class WebSocketChatMessage(BaseModel):
    """WebSocket聊天消息模型"""

    type: str = "chat"  # chat, ping等
    message: str | None = None
    agent_id: str | None = None
    conversation_id: str | None = None
    model_id: str | None = None
    user_id: str | None = None
    timestamp: str | None = None


class WebSocketResponse(BaseModel):
    """WebSocket响应模型"""

    type: str  # connection_success, chat_start, agent_event, chat_complete, error等
    message: str | None = None
    data: dict | None = None
    timestamp: str | None = None


class WebSocketEventMessage(BaseModel):
    """WebSocket事件消息模型"""

    type: str  # agent_event, status_update等
    event_type: str | None = None  # 具体的事件类型
    agent_name: str | None = None
    data: dict | None = None
    timestamp: str | None = None
    sequence: int | None = None


class WebSocketStatusUpdate(BaseModel):
    """WebSocket状态更新消息"""

    type: str = "status_update"
    status: str  # processing, thinking, tool_calling, completed等
    message: str | None = None
    timestamp: str | None = None


class WebSocketChatComplete(BaseModel):
    """WebSocket聊天完成消息"""

    type: str = "chat_complete"
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    response: str
    model_used: str | None = None
    tools_available: int = 0
    events_count: int = 0
    timestamp: str | None = None


class WebSocketErrorMessage(BaseModel):
    """WebSocket错误消息"""

    type: str = "error"
    message: str
    timestamp: str | None = None
    error_code: str | None = None


class RealtimeEventSummary(BaseModel):
    """实时事件摘要"""

    total_events: int = 0
    event_types: dict[str, int] = {}
    timeline: list[tuple[str, str]] = []
    realtime_enabled: bool = True


class AgentDialogueResultWithRealtime(BaseModel):
    """包含实时事件的Agent对话结果"""

    success: bool
    response: str | None = None
    error: str | None = None
    raw_result: dict | None = None
    agent_name: str | None = None
    events: list[AgentEventPublic] | None = None
    events_summary: RealtimeEventSummary | None = None
    session_id: str | None = None
    autoagent_messages: list[dict] | None = None
    context_variables: dict | None = None
    fallback_used: bool = False
    realtime_events: bool = True
    model_used: str | None = None
    tools_available: int = 0
