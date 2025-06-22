import uuid

from sqlmodel import Session, select

from app.models import LLMConfig
from app.schemas import LLMConfigCreate, LLMConfigUpdate
from app.utils.encryption import encrypt_text, decrypt_text


def create_llm_config(
    *, session: Session, llm_config_create: LLMConfigCreate, user_id: uuid.UUID
) -> LLMConfig:
    """创建新的LLM配置"""
    # 加密API密钥
    encrypted_api_key = encrypt_text(llm_config_create.api_key)

    # 创建数据字典
    llm_config_data = llm_config_create.model_dump()
    llm_config_data.pop("api_key")  # 移除明文密钥
    llm_config_data["api_key_encrypted"] = encrypted_api_key
    llm_config_data["user_id"] = user_id

    db_obj = LLMConfig.model_validate(llm_config_data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_llm_config_by_id(*, session: Session, llm_id: uuid.UUID) -> LLMConfig | None:
    """根据ID获取LLM配置"""
    statement = select(LLMConfig).where(LLMConfig.llm_id == llm_id)
    return session.exec(statement).first()


def get_llm_configs_by_user(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[LLMConfig]:
    """获取用户的所有LLM配置"""
    statement = (
        select(LLMConfig).where(LLMConfig.user_id == user_id).offset(skip).limit(limit)
    )
    return list(session.exec(statement).all())


def get_llm_config_by_provider(
    *, session: Session, user_id: uuid.UUID, provider: str
) -> LLMConfig | None:
    """根据提供商获取用户的LLM配置"""
    statement = select(LLMConfig).where(
        LLMConfig.user_id == user_id, LLMConfig.provider == provider
    )
    return session.exec(statement).first()


def update_llm_config(
    *, session: Session, db_llm_config: LLMConfig, llm_config_in: LLMConfigUpdate
) -> LLMConfig:
    """更新LLM配置"""
    llm_config_data = llm_config_in.model_dump(exclude_unset=True)

    # 如果包含新的API密钥，需要加密
    if "api_key" in llm_config_data:
        encrypted_api_key = encrypt_text(llm_config_data["api_key"])
        llm_config_data["api_key_encrypted"] = encrypted_api_key
        del llm_config_data["api_key"]  # 删除明文密钥

    db_llm_config.sqlmodel_update(llm_config_data)
    session.add(db_llm_config)
    session.commit()
    session.refresh(db_llm_config)
    return db_llm_config


def delete_llm_config(*, session: Session, llm_id: uuid.UUID) -> bool:
    """删除LLM配置"""
    llm_config = session.get(LLMConfig, llm_id)
    if llm_config:
        session.delete(llm_config)
        session.commit()
        return True
    return False


def get_decrypted_api_key(*, session: Session, llm_id: uuid.UUID) -> str | None:
    """获取解密后的API密钥（用于内部使用）"""
    llm_config = session.get(LLMConfig, llm_id)
    if llm_config and llm_config.api_key_encrypted:
        return decrypt_text(llm_config.api_key_encrypted)
    return None


def get_llm_configs_count_by_user(*, session: Session, user_id: uuid.UUID) -> int:
    """获取用户LLM配置总数"""
    statement = select(LLMConfig).where(LLMConfig.user_id == user_id)
    return len(list(session.exec(statement).all()))
