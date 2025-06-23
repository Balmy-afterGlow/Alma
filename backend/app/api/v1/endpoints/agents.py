"""
Agent管理API端点
处理系统Agent的查看和工具查看（只读）
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, SessionDep
from app.db.repository import (
    get_agent_by_id,
    get_system_agents,
    get_tools_by_agent,
)
from app.models import User
from app.schemas import AgentPublic, AgentsPublic, ToolsPublic

router = APIRouter()


@router.get("/system", response_model=AgentsPublic)
def get_available_system_agents(
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> AgentsPublic:
    """获取可用的系统Agent列表"""
    agents = get_system_agents(session=session, skip=skip, limit=limit)
    return AgentsPublic(data=agents, count=len(agents))


@router.get("/{agent_id}", response_model=AgentPublic)
def get_agent_details(
    agent_id: uuid.UUID,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AgentPublic:
    """获取Agent详细信息"""
    agent = get_agent_by_id(session=session, agent_id=agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent不存在")

    # 只允许查看系统Agent
    if not agent.is_system_agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只能查看系统Agent"
        )

    return agent


@router.get("/{agent_id}/tools", response_model=ToolsPublic)
def get_agent_tools(
    agent_id: uuid.UUID,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ToolsPublic:
    """获取Agent的工具列表"""
    # 先检查Agent是否存在且为系统Agent
    agent = get_agent_by_id(session=session, agent_id=agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent不存在")

    if not agent.is_system_agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只能查看系统Agent的工具"
        )

    tools = get_tools_by_agent(session=session, agent_id=agent_id)
    return ToolsPublic(data=tools, count=len(tools))
