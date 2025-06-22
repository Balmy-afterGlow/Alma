import uuid

from sqlmodel import Session, select

from app.models import Agent
from app.schemas import AgentCreate, AgentUpdate


def create_agent(
    *, session: Session, agent_create: AgentCreate, user_id: uuid.UUID
) -> Agent:
    """创建新的智能体"""
    db_obj = Agent.model_validate(agent_create, update={"user_id": user_id})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_agent_by_id(*, session: Session, agent_id: uuid.UUID) -> Agent | None:
    """根据ID获取智能体"""
    statement = select(Agent).where(Agent.agent_id == agent_id)
    return session.exec(statement).first()


def get_agents_by_user(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Agent]:
    """获取用户的所有智能体"""
    statement = select(Agent).where(Agent.user_id == user_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_system_agents(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Agent]:
    """获取系统智能体"""
    statement = (
        select(Agent)
        .where(Agent.is_system_agent)
        .where(Agent.status == "active")
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_agent(*, session: Session, db_agent: Agent, agent_in: AgentUpdate) -> Agent:
    """更新智能体"""
    agent_data = agent_in.model_dump(exclude_unset=True)
    db_agent.sqlmodel_update(agent_data)
    session.add(db_agent)
    session.commit()
    session.refresh(db_agent)
    return db_agent


def delete_agent(*, session: Session, agent_id: uuid.UUID) -> bool:
    """删除智能体"""
    agent = session.get(Agent, agent_id)
    if agent:
        session.delete(agent)
        session.commit()
        return True
    return False


def get_agents_count_by_user(*, session: Session, user_id: uuid.UUID) -> int:
    """获取用户智能体总数"""
    statement = select(Agent).where(Agent.user_id == user_id)
    return len(list(session.exec(statement).all()))


def get_active_agents_by_user(*, session: Session, user_id: uuid.UUID) -> list[Agent]:
    """获取用户的活跃智能体"""
    statement = (
        select(Agent).where(Agent.user_id == user_id).where(Agent.status == "active")
    )
    return list(session.exec(statement).all())
