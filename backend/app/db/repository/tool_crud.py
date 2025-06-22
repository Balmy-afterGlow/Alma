import uuid

from sqlmodel import Session, select

from app.models import Tool
from app.schemas import ToolCreate, ToolUpdate


def create_tool(*, session: Session, tool_create: ToolCreate) -> Tool:
    """创建新的工具"""
    db_obj = Tool.model_validate(tool_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_tool_by_id(*, session: Session, tool_id: uuid.UUID) -> Tool | None:
    """根据ID获取工具"""
    statement = select(Tool).where(Tool.tool_id == tool_id)
    return session.exec(statement).first()


def get_tool_by_name(*, session: Session, name: str) -> Tool | None:
    """根据名称获取工具"""
    statement = select(Tool).where(Tool.name == name)
    return session.exec(statement).first()


def get_all_tools(*, session: Session, skip: int = 0, limit: int = 100) -> list[Tool]:
    """获取所有工具"""
    statement = select(Tool).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_tool(*, session: Session, db_tool: Tool, tool_in: ToolUpdate) -> Tool:
    """更新工具"""
    tool_data = tool_in.model_dump(exclude_unset=True)
    db_tool.sqlmodel_update(tool_data)
    session.add(db_tool)
    session.commit()
    session.refresh(db_tool)
    return db_tool


def delete_tool(*, session: Session, tool_id: uuid.UUID) -> bool:
    """删除工具"""
    tool = session.get(Tool, tool_id)
    if tool:
        session.delete(tool)
        session.commit()
        return True
    return False


def search_tools_by_name(
    *, session: Session, search_term: str, limit: int = 50
) -> list[Tool]:
    """根据名称搜索工具"""
    tools = session.exec(select(Tool)).all()
    matching_tools = []

    for tool in tools:
        if search_term.lower() in tool.name.lower():
            matching_tools.append(tool)
            if len(matching_tools) >= limit:
                break

    return matching_tools


def get_tools_count(*, session: Session) -> int:
    """获取工具总数"""
    statement = select(Tool)
    return len(list(session.exec(statement).all()))
