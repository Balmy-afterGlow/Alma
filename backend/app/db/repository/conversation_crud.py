import uuid

from sqlmodel import Session, select, desc

from app.models import Conversation
from app.schemas import ConversationCreate, ConversationUpdate


def create_conversation(
    *, session: Session, conversation_create: ConversationCreate, user_id: uuid.UUID
) -> Conversation:
    """创建新的对话"""
    db_obj = Conversation.model_validate(
        conversation_create, update={"user_id": user_id}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_conversation_by_id(
    *, session: Session, conversation_id: uuid.UUID
) -> Conversation | None:
    """根据ID获取对话"""
    statement = select(Conversation).where(
        Conversation.conversation_id == conversation_id
    )
    return session.exec(statement).first()


def get_conversations_by_user(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Conversation]:
    """获取用户的所有对话"""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(desc(Conversation.created_at))
    )
    return list(session.exec(statement).all())


def update_conversation(
    *,
    session: Session,
    db_conversation: Conversation,
    conversation_in: ConversationUpdate,
) -> Conversation:
    """更新对话"""
    conversation_data = conversation_in.model_dump(exclude_unset=True)
    db_conversation.sqlmodel_update(conversation_data)
    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)
    return db_conversation


def delete_conversation(*, session: Session, conversation_id: uuid.UUID) -> bool:
    """删除对话"""
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        session.delete(conversation)
        session.commit()
        return True
    return False


def get_conversations_count_by_user(*, session: Session, user_id: uuid.UUID) -> int:
    """获取用户对话总数"""
    statement = select(Conversation).where(Conversation.user_id == user_id)
    return len(list(session.exec(statement).all()))


def get_recent_conversations_by_user(
    *, session: Session, user_id: uuid.UUID, limit: int = 10
) -> list[Conversation]:
    """获取用户最近的对话"""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.created_at))
        .limit(limit)
    )
    return list(session.exec(statement).all())
