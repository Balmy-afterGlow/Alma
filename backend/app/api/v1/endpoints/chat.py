"""
聊天交互API端点
处理用户与Agent的实时对话交互
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, get_session
from app.db.repository import (
    create_conversation,
    create_message,
    get_agent_by_id,
    get_conversation_by_id,
    get_decrypted_api_key,
    get_model_by_id,
)
from app.models import User
from app.schemas import ConversationCreate, MessageCreate

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


@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    *,
    session: Annotated[Session, Depends(get_session)],
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

    # 4. 获取模型和API密钥信息（如果指定了模型）
    model = None
    if chat_request.model_id:
        model = get_model_by_id(session=session, model_id=chat_request.model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在"
            )

        # 检查模型是否属于当前用户的LLM配置
        api_key = get_decrypted_api_key(session=session, llm_id=model.llm_id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无法访问模型的API密钥"
            )

    # 5. 调用LLM生成响应（这里需要实现具体的LLM调用逻辑）
    # TODO: 实现实际的LLM调用逻辑
    assistant_response = await _generate_agent_response(
        agent=agent, user_message=chat_request.message, model=model
    )

    # 6. 创建助手消息
    assistant_message = create_message(
        session=session,
        message_create=MessageCreate(
            role="assistant",
            content=assistant_response,
            conversation_id=conversation.conversation_id,
            agent_id=chat_request.agent_id,
            model_metadata={
                "model_id": str(chat_request.model_id)
                if chat_request.model_id
                else None,
                "model_name": model.name if model else None,
            },
        ),
    )

    return ChatResponse(
        conversation_id=conversation.conversation_id,
        user_message_id=user_message.message_id,
        assistant_message_id=assistant_message.message_id,
        response=assistant_response,
    )


async def _generate_agent_response(agent, user_message: str, model=None) -> str:
    """生成Agent响应的内部函数"""
    # TODO: 这里需要实现实际的LLM调用逻辑
    # 目前返回一个简单的模拟响应

    response = f"我是{agent.name}。收到你的消息：'{user_message}'。"

    if model:
        response += f" 我正在使用{model.name}模型为你服务。"

    # 这里应该根据agent.instruction和用户消息来构建prompt
    # 然后调用相应的LLM API
    # 示例实现：
    # - 构建完整的prompt（包含agent instruction、工具信息等）
    # - 调用LLM API
    # - 处理工具调用（如果有）
    # - 返回最终响应

    return response
