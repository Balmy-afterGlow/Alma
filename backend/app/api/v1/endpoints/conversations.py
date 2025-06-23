"""
对话管理API端点
处理用户的对话创建、查看、更新和删除
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, SessionDep
from app.db.repository import (
    create_conversation,
    delete_conversation,
    get_agent_by_id,
    get_conversation_by_id,
    get_conversations_by_user,
    get_messages_by_conversation,
    get_recent_conversations_by_user,
    update_conversation,
)
from app.models import User
from app.schemas import (
    ConversationCreate,
    ConversationPublic,
    ConversationsPublic,
    ConversationUpdate,
    ConversationWithEventsMessages,
    AgentEventPublic,
    ChatMessageWithEvents,
)

router = APIRouter()


@router.get("/", response_model=ConversationsPublic)
def get_user_conversations(
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> ConversationsPublic:
    """获取当前用户的所有对话"""
    conversations = get_conversations_by_user(
        session=session, user_id=current_user.user_id, skip=skip, limit=limit
    )
    return ConversationsPublic(data=conversations, count=len(conversations))


@router.get("/recent", response_model=ConversationsPublic)
def get_recent_conversations(
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
) -> ConversationsPublic:
    """获取当前用户的最近对话（用于侧边栏）"""
    conversations = get_recent_conversations_by_user(
        session=session, user_id=current_user.user_id, limit=limit
    )
    return ConversationsPublic(data=conversations, count=len(conversations))


@router.post("/", response_model=ConversationPublic)
def create_new_conversation(
    *,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    conversation_in: ConversationCreate,
) -> ConversationPublic:
    """创建新的对话"""
    conversation = create_conversation(
        session=session,
        conversation_create=conversation_in,
        user_id=current_user.user_id,
    )
    return conversation


@router.get("/{conversation_id}", response_model=ConversationPublic)
def get_conversation(
    conversation_id: uuid.UUID,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConversationPublic:
    """获取指定对话的详细信息"""
    conversation = get_conversation_by_id(
        session=session, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    # 检查权限：只能访问自己的对话
    if conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此对话"
        )

    return conversation


@router.put("/{conversation_id}", response_model=ConversationPublic)
def update_conversation_title(
    *,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    conversation_id: uuid.UUID,
    conversation_in: ConversationUpdate,
) -> ConversationPublic:
    """更新对话标题"""
    conversation = get_conversation_by_id(
        session=session, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    # 检查权限
    if conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此对话"
        )

    conversation = update_conversation(
        session=session, db_conversation=conversation, conversation_in=conversation_in
    )
    return conversation


@router.delete("/{conversation_id}")
def delete_user_conversation(
    conversation_id: uuid.UUID,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """删除对话"""
    conversation = get_conversation_by_id(
        session=session, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    # 检查权限
    if conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此对话"
        )

    success = delete_conversation(session=session, conversation_id=conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除对话失败"
        )

    return {"message": "对话删除成功"}


@router.get(
    "/{conversation_id}/detailed", response_model=ConversationWithEventsMessages
)
def get_conversation_detailed(
    *,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    conversation_id: uuid.UUID,
) -> ConversationWithEventsMessages:
    """获取包含详细事件信息的对话内容"""

    conversation = get_conversation_by_id(
        session=session, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    if conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此对话"
        )

    # 获取消息列表
    messages = get_messages_by_conversation(
        session=session, conversation_id=conversation_id
    )

    # 构建包含事件信息的消息列表
    detailed_messages = []
    for message in messages:
        # 从model_metadata中提取事件信息
        events_data = (
            message.model_metadata.get("events", []) if message.model_metadata else []
        )
        events = [
            AgentEventPublic(
                event_type=event.get("event_type", ""),
                timestamp=event.get("timestamp", ""),
                agent_name=event.get("agent_name", ""),
                data=event.get("data", {}),
            )
            for event in events_data
        ]

        agent = get_agent_by_id(session=session, agent_id=message.agent_id)

        detailed_message = ChatMessageWithEvents(
            message_id=message.message_id,
            role=message.role,
            content=message.content,
            timestamp=message.timestamp,
            agent_id=message.agent_id,
            agent_name=agent.name if agent else None,
            model_metadata=message.model_metadata,
            events=events,
            model_used=message.model_metadata.get("model_name")
            if message.model_metadata
            else None,
            tools_available=message.model_metadata.get("tools_available", 0)
            if message.model_metadata
            else 0,
        )
        detailed_messages.append(detailed_message)

    return ConversationWithEventsMessages(
        conversation_id=conversation.conversation_id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=detailed_messages,
        messages_count=len(detailed_messages),
    )
