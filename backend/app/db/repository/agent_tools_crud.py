import uuid

from sqlmodel import Session, select

from app.models import AgentTools, Agent, Tool


def add_tool_to_agent(
    *, session: Session, agent_id: uuid.UUID, tool_id: uuid.UUID
) -> AgentTools:
    """为智能体添加工具"""
    # 检查关联是否已存在
    existing = session.exec(
        select(AgentTools).where(
            AgentTools.agent_id == agent_id, AgentTools.tool_id == tool_id
        )
    ).first()

    if existing:
        return existing

    db_obj = AgentTools(agent_id=agent_id, tool_id=tool_id)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def remove_tool_from_agent(
    *, session: Session, agent_id: uuid.UUID, tool_id: uuid.UUID
) -> bool:
    """从智能体中移除工具"""
    agent_tool = session.exec(
        select(AgentTools).where(
            AgentTools.agent_id == agent_id, AgentTools.tool_id == tool_id
        )
    ).first()

    if agent_tool:
        session.delete(agent_tool)
        session.commit()
        return True
    return False


def get_tools_by_agent(*, session: Session, agent_id: uuid.UUID) -> list[Tool]:
    """获取智能体的所有工具"""
    # 先获取智能体关联的工具ID
    agent_tools = session.exec(
        select(AgentTools).where(AgentTools.agent_id == agent_id)
    ).all()

    if not agent_tools:
        return []

    tool_ids = [at.tool_id for at in agent_tools]

    # 根据工具ID获取工具
    tools = []
    for tool_id in tool_ids:
        tool = session.get(Tool, tool_id)
        if tool:
            tools.append(tool)

    return tools


def get_agents_by_tool(*, session: Session, tool_id: uuid.UUID) -> list[Agent]:
    """获取使用该工具的所有智能体"""
    # 先获取使用该工具的智能体ID
    agent_tools = session.exec(
        select(AgentTools).where(AgentTools.tool_id == tool_id)
    ).all()

    if not agent_tools:
        return []

    agent_ids = [at.agent_id for at in agent_tools]

    # 根据智能体ID获取智能体
    agents = []
    for agent_id in agent_ids:
        agent = session.get(Agent, agent_id)
        if agent:
            agents.append(agent)

    return agents


def get_agent_tool_relationships(
    *, session: Session, agent_id: uuid.UUID
) -> list[AgentTools]:
    """获取智能体的所有工具关联"""
    statement = select(AgentTools).where(AgentTools.agent_id == agent_id)
    return list(session.exec(statement).all())


def clear_agent_tools(*, session: Session, agent_id: uuid.UUID) -> bool:
    """清除智能体的所有工具关联"""
    agent_tools = session.exec(
        select(AgentTools).where(AgentTools.agent_id == agent_id)
    ).all()

    for agent_tool in agent_tools:
        session.delete(agent_tool)

    session.commit()
    return True


def set_agent_tools(
    *, session: Session, agent_id: uuid.UUID, tool_ids: list[uuid.UUID]
) -> list[AgentTools]:
    """设置智能体的工具（替换现有的所有工具）"""
    # 先清除现有的工具关联
    clear_agent_tools(session=session, agent_id=agent_id)

    # 添加新的工具关联
    result = []
    for tool_id in tool_ids:
        agent_tool = add_tool_to_agent(
            session=session, agent_id=agent_id, tool_id=tool_id
        )
        result.append(agent_tool)

    return result


def count_tools_for_agent(*, session: Session, agent_id: uuid.UUID) -> int:
    """计算智能体拥有的工具数量"""
    statement = select(AgentTools).where(AgentTools.agent_id == agent_id)
    return len(list(session.exec(statement).all()))


def count_agents_for_tool(*, session: Session, tool_id: uuid.UUID) -> int:
    """计算使用该工具的智能体数量"""
    statement = select(AgentTools).where(AgentTools.tool_id == tool_id)
    return len(list(session.exec(statement).all()))
