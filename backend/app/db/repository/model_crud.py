import uuid

from sqlmodel import Session, select

from app.models import Model
from app.schemas import ModelCreate, ModelUpdate


def create_model(*, session: Session, model_create: ModelCreate) -> Model:
    """创建新的模型"""
    db_obj = Model.model_validate(model_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_model_by_id(*, session: Session, model_id: uuid.UUID) -> Model | None:
    """根据ID获取模型"""
    statement = select(Model).where(Model.model_id == model_id)
    return session.exec(statement).first()


def get_models_by_llm_config(
    *, session: Session, llm_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Model]:
    """获取LLM配置下的所有模型"""
    statement = select(Model).where(Model.llm_id == llm_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_model_by_name(
    *, session: Session, name: str, llm_id: uuid.UUID
) -> Model | None:
    """根据名称和LLM配置ID获取模型"""
    statement = select(Model).where(Model.name == name, Model.llm_id == llm_id)
    return session.exec(statement).first()


def update_model(*, session: Session, db_model: Model, model_in: ModelUpdate) -> Model:
    """更新模型"""
    model_data = model_in.model_dump(exclude_unset=True)
    db_model.sqlmodel_update(model_data)
    session.add(db_model)
    session.commit()
    session.refresh(db_model)
    return db_model


def delete_model(*, session: Session, model_id: uuid.UUID) -> bool:
    """删除模型"""
    model = session.get(Model, model_id)
    if model:
        session.delete(model)
        session.commit()
        return True
    return False


def get_all_models(*, session: Session, skip: int = 0, limit: int = 100) -> list[Model]:
    """获取所有模型"""
    statement = select(Model).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_models_count_by_llm_config(*, session: Session, llm_id: uuid.UUID) -> int:
    """获取LLM配置下的模型总数"""
    statement = select(Model).where(Model.llm_id == llm_id)
    return len(list(session.exec(statement).all()))
