"""
消息管理API端点
处理对话中的消息创建、查看、更新和删除
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, get_session
from app.db.repository import (
    create_message,
    get_conversation_by_id,
    get_message_by_id,
    get_messages_by_conversation,
    soft_delete_message,
    update_message,
)
from app.models import User
from app.schemas import MessageCreate, MessagePublic, MessagesPublic, MessageUpdate

router = APIRouter()


@router.get("/conversation/{conversation_id}", response_model=MessagesPublic)
def get_conversation_messages(
    conversation_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> MessagesPublic:
    """获取对话中的所有消息"""
    # 先检查对话是否存在且属于当前用户
    conversation = get_conversation_by_id(
        session=session, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    if conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此对话"
        )

    messages = get_messages_by_conversation(
        session=session, conversation_id=conversation_id, skip=skip, limit=limit
    )
    return MessagesPublic(data=messages, count=len(messages))


@router.post("/", response_model=MessagePublic)
def create_new_message(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    message_in: MessageCreate,
) -> MessagePublic:
    """创建新消息"""
    # 检查对话权限
    conversation = get_conversation_by_id(
        session=session, conversation_id=message_in.conversation_id
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

    if conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权在此对话中创建消息"
        )

    # 创建消息
    message = create_message(session=session, message_create=message_in)
    return message


@router.get("/{message_id}", response_model=MessagePublic)
def get_message(
    message_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MessagePublic:
    """获取指定消息"""
    message = get_message_by_id(session=session, message_id=message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    # 通过对话检查权限
    conversation = get_conversation_by_id(
        session=session, conversation_id=message.conversation_id
    )
    if not conversation or conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此消息"
        )

    return message


@router.put("/{message_id}", response_model=MessagePublic)
def update_user_message(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    message_id: uuid.UUID,
    message_in: MessageUpdate,
) -> MessagePublic:
    """更新消息（通常只允许编辑自己发送的消息）"""
    message = get_message_by_id(session=session, message_id=message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    # 检查权限
    conversation = get_conversation_by_id(
        session=session, conversation_id=message.conversation_id
    )
    if not conversation or conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此消息"
        )

    # 通常只允许修改用户自己的消息
    if message.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只能修改用户消息"
        )

    message = update_message(session=session, db_message=message, message_in=message_in)
    return message


@router.delete("/{message_id}")
def delete_user_message(
    message_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """删除消息（软删除）"""
    message = get_message_by_id(session=session, message_id=message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    # 检查权限
    conversation = get_conversation_by_id(
        session=session, conversation_id=message.conversation_id
    )
    if not conversation or conversation.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此消息"
        )

    success = soft_delete_message(session=session, message_id=message_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除消息失败"
        )

    return {"message": "消息删除成功"}
