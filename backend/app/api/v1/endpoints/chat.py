"""
聊天交互API端点
处理用户与Agent的实时对话交互
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, SessionDep
from app.db.repository import (
    create_conversation,
    create_message,
    get_agent_by_id,
    get_conversation_by_id,
    get_model_by_id,
    get_messages_by_conversation,
)
from app.models import User
from app.schemas import ConversationCreate, MessageCreate
from app.services.agent_service import agent_dialogue_service

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求模型"""

    message: str
    agent_id: uuid.UUID
    conversation_id: uuid.UUID | None = None
    model_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    """聊天响应模型"""

    conversation_id: uuid.UUID
    user_message_id: uuid.UUID
    assistant_message_id: uuid.UUID
    response: str
    events: list[dict] | None = None
    events_summary: dict | None = None
    session_id: str | None = None
    autoagent_info: dict | None = None


@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    *,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    chat_request: ChatRequest,
) -> ChatResponse:
    """与Agent进行对话"""

    # 1. 验证Agent存在且为系统Agent
    agent = get_agent_by_id(session=session, agent_id=chat_request.agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent不存在")

    if not agent.is_system_agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只能与系统Agent对话"
        )

    # 2. 处理对话
    conversation = None
    if chat_request.conversation_id:
        # 使用现有对话
        conversation = get_conversation_by_id(
            session=session, conversation_id=chat_request.conversation_id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在"
            )

        if conversation.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此对话"
            )
    else:
        # 创建新对话
        conversation_create = ConversationCreate(title="新对话")
        conversation = create_conversation(
            session=session,
            conversation_create=conversation_create,
            user_id=current_user.user_id,
        )

    # 3. 创建用户消息
    user_message = create_message(
        session=session,
        message_create=MessageCreate(
            role="user",
            content=chat_request.message,
            conversation_id=conversation.conversation_id,
            agent_id=chat_request.agent_id,
        ),
    )

    # 4. 获取模型信息（如果指定了模型）
    model = None
    if chat_request.model_id:
        model = get_model_by_id(session=session, model_id=chat_request.model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在"
            )

    # 5. 获取对话历史
    conversation_history = get_messages_by_conversation(
        session=session, conversation_id=conversation.conversation_id
    )

    # 6. 调用智能体对话服务，使用AutoAgent
    session_id = str(conversation.conversation_id)
    dialogue_result = await agent_dialogue_service.process_agent_dialogue(
        session=session,
        agent=agent,
        user_message=chat_request.message,
        conversation_history=conversation_history[:-1],  # 排除刚创建的用户消息
        session_id=session_id,
    )

    if not dialogue_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话处理失败: {dialogue_result.get('error', '未知错误')}",
        )

    # 7. 创建助手消息
    assistant_message = create_message(
        session=session,
        message_create=MessageCreate(
            role="assistant",
            content=dialogue_result["response"],
            conversation_id=conversation.conversation_id,
            agent_id=chat_request.agent_id,
            model_metadata={
                "model_id": str(chat_request.model_id)
                if chat_request.model_id
                else None,
                "model_name": model.name if model else None,
                "events": dialogue_result.get("events", []),
                "events_summary": dialogue_result.get("events_summary", {}),
                "session_id": dialogue_result.get("session_id"),
                "autoagent_info": {
                    "agent_name": dialogue_result.get("agent_name"),
                    "raw_result": dialogue_result.get("raw_result"),
                    "autoagent_messages": dialogue_result.get("autoagent_messages", []),
                },
            },
        ),
    )

    return ChatResponse(
        conversation_id=conversation.conversation_id,
        user_message_id=user_message.message_id,
        assistant_message_id=assistant_message.message_id,
        response=dialogue_result["response"],
        events=dialogue_result.get("events"),
        events_summary=dialogue_result.get("events_summary"),
        session_id=dialogue_result.get("session_id"),
        autoagent_info={
            "agent_name": dialogue_result.get("agent_name"),
            "context_variables": dialogue_result.get("context_variables", {}),
        },
    )
