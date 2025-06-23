"""
仪表板API端点
提供用户概览信息和统计数据
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, SessionDep
from app.db.repository import (
    get_conversations_count_by_user,
    get_llm_configs_count_by_user,
    get_recent_conversations_by_user,
    get_system_agents,
)
from app.models import User
from app.schemas.chat import UserDashboard

router = APIRouter()


@router.get("/", response_model=UserDashboard)
def get_user_dashboard(
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserDashboard:
    """获取用户仪表板数据"""

    # 获取统计信息
    llm_configs_count = get_llm_configs_count_by_user(
        session=session, user_id=current_user.user_id
    )
    conversations_count = get_conversations_count_by_user(
        session=session, user_id=current_user.user_id
    )

    # 获取最近的对话
    recent_conversations_data = get_recent_conversations_by_user(
        session=session, user_id=current_user.user_id, limit=5
    )
    recent_conversations = [
        {
            "conversation_id": str(conv.conversation_id),
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
        }
        for conv in recent_conversations_data
    ]

    # 获取可用的系统Agent
    available_agents_data = get_system_agents(session=session, limit=10)
    available_agents = [
        {
            "agent_id": str(agent.agent_id),
            "name": agent.name,
            "instruction": agent.instruction[:100] + "..."
            if len(agent.instruction) > 100
            else agent.instruction,
            "status": agent.status,
        }
        for agent in available_agents_data
    ]

    return UserDashboard(
        llm_configs_count=llm_configs_count,
        conversations_count=conversations_count,
        recent_conversations=recent_conversations,
        available_agents=available_agents,
    )
