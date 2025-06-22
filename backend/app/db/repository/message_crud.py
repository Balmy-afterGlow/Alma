import uuid

from sqlmodel import Session, select, desc

from app.models import Message
from app.schemas import MessageCreate, MessageUpdate


def create_message(*, session: Session, message_create: MessageCreate) -> Message:
    """创建新的消息"""
    db_obj = Message.model_validate(message_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_message_by_id(*, session: Session, message_id: uuid.UUID) -> Message | None:
    """根据ID获取消息"""
    statement = select(Message).where(Message.message_id == message_id)
    return session.exec(statement).first()


def get_messages_by_conversation(
    *, session: Session, conversation_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Message]:
    """获取对话中的所有消息"""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.is_deleted != True)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_messages_by_agent(
    *, session: Session, agent_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Message]:
    """获取智能体的所有消息"""
    statement = (
        select(Message)
        .where(Message.agent_id == agent_id)
        .where(Message.is_deleted != True)
        .offset(skip)
        .limit(limit)
        .order_by(desc(Message.timestamp))
    )
    return list(session.exec(statement).all())


def update_message(
    *, session: Session, db_message: Message, message_in: MessageUpdate
) -> Message:
    """更新消息"""
    message_data = message_in.model_dump(exclude_unset=True)
    db_message.sqlmodel_update(message_data)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return db_message


def soft_delete_message(*, session: Session, message_id: uuid.UUID) -> bool:
    """软删除消息（标记为已删除）"""
    message = session.get(Message, message_id)
    if message:
        message.is_deleted = True
        session.add(message)
        session.commit()
        return True
    return False


def hard_delete_message(*, session: Session, message_id: uuid.UUID) -> bool:
    """硬删除消息（从数据库中彻底删除）"""
    message = session.get(Message, message_id)
    if message:
        session.delete(message)
        session.commit()
        return True
    return False


def get_messages_count_by_conversation(
    *, session: Session, conversation_id: uuid.UUID
) -> int:
    """获取对话中的消息总数"""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.is_deleted != True)
    )
    return len(list(session.exec(statement).all()))


def get_latest_message_by_conversation(
    *, session: Session, conversation_id: uuid.UUID
) -> Message | None:
    """获取对话中的最新消息"""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.is_deleted != True)
        .order_by(desc(Message.timestamp))
        .limit(1)
    )
    return session.exec(statement).first()


def search_messages_by_content(
    *, session: Session, conversation_id: uuid.UUID, search_term: str, limit: int = 50
) -> list[Message]:
    """在对话中搜索包含特定内容的消息"""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.is_deleted != True)
        .order_by(desc(Message.timestamp))
    )
    all_messages = list(session.exec(statement).all())

    matching_messages = []
    for message in all_messages:
        if search_term.lower() in message.content.lower():
            matching_messages.append(message)
            if len(matching_messages) >= limit:
                break

    return matching_messages
