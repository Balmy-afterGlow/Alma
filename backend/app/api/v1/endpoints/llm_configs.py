"""
LLM配置管理API端点
处理用户的LLM配置和模型管理
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, get_session
from app.db.repository import (
    create_llm_config,
    create_model,
    delete_llm_config,
    delete_model,
    get_llm_config_by_id,
    get_llm_configs_by_user,
    get_models_by_llm_config,
    update_llm_config,
    update_model,
)
from app.models import User
from app.schemas import (
    LLMConfigCreate,
    LLMConfigPublic,
    LLMConfigsPublic,
    LLMConfigUpdate,
    ModelCreate,
    ModelPublic,
    ModelsPublic,
    ModelUpdate,
)

router = APIRouter()


@router.get("/", response_model=LLMConfigsPublic)
def get_user_llm_configs(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> LLMConfigsPublic:
    """获取当前用户的所有LLM配置"""
    llm_configs = get_llm_configs_by_user(
        session=session, user_id=current_user.user_id, skip=skip, limit=limit
    )
    return LLMConfigsPublic(data=llm_configs, count=len(llm_configs))


@router.post("/", response_model=LLMConfigPublic)
def create_user_llm_config(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    llm_config_in: LLMConfigCreate,
) -> LLMConfigPublic:
    """创建新的LLM配置"""
    llm_config = create_llm_config(
        session=session, llm_config_create=llm_config_in, user_id=current_user.user_id
    )
    return llm_config


@router.get("/{llm_id}", response_model=LLMConfigPublic)
def get_llm_config(
    llm_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LLMConfigPublic:
    """获取指定的LLM配置"""
    llm_config = get_llm_config_by_id(session=session, llm_id=llm_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM配置不存在"
        )

    # 检查权限：只能访问自己的LLM配置
    if llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此LLM配置"
        )

    return llm_config


@router.put("/{llm_id}", response_model=LLMConfigPublic)
def update_user_llm_config(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    llm_id: uuid.UUID,
    llm_config_in: LLMConfigUpdate,
) -> LLMConfigPublic:
    """更新LLM配置"""
    llm_config = get_llm_config_by_id(session=session, llm_id=llm_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM配置不存在"
        )

    # 检查权限
    if llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此LLM配置"
        )

    llm_config = update_llm_config(
        session=session, db_llm_config=llm_config, llm_config_in=llm_config_in
    )
    return llm_config


@router.delete("/{llm_id}")
def delete_user_llm_config(
    llm_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """删除LLM配置"""
    llm_config = get_llm_config_by_id(session=session, llm_id=llm_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM配置不存在"
        )

    # 检查权限
    if llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此LLM配置"
        )

    success = delete_llm_config(session=session, llm_id=llm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除LLM配置失败"
        )

    return {"message": "LLM配置删除成功"}


# 模型管理端点
@router.get("/{llm_id}/models", response_model=ModelsPublic)
def get_llm_models(
    llm_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> ModelsPublic:
    """获取LLM配置下的所有模型"""
    # 先检查LLM配置是否存在且属于当前用户
    llm_config = get_llm_config_by_id(session=session, llm_id=llm_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM配置不存在"
        )

    if llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此LLM配置"
        )

    models = get_models_by_llm_config(
        session=session, llm_id=llm_id, skip=skip, limit=limit
    )
    return ModelsPublic(data=models, count=len(models))


@router.post("/{llm_id}/models", response_model=ModelPublic)
def create_llm_model(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    llm_id: uuid.UUID,
    model_in: ModelCreate,
) -> ModelPublic:
    """为LLM配置创建新模型"""
    # 检查LLM配置权限
    llm_config = get_llm_config_by_id(session=session, llm_id=llm_id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM配置不存在"
        )

    if llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权在此LLM配置下创建模型"
        )

    # 创建模型，确保llm_id正确
    model_data = model_in.model_copy(update={"llm_id": llm_id})
    model = create_model(session=session, model_create=model_data)
    return model


@router.put("/{llm_id}/models/{model_id}", response_model=ModelPublic)
def update_llm_model(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    llm_id: uuid.UUID,
    model_id: uuid.UUID,
    model_in: ModelUpdate,
) -> ModelPublic:
    """更新模型"""
    # 检查权限（通过LLM配置检查）
    llm_config = get_llm_config_by_id(session=session, llm_id=llm_id)
    if not llm_config or llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此模型"
        )

    from app.db.repository import get_model_by_id

    model = get_model_by_id(session=session, model_id=model_id)
    if not model or model.llm_id != llm_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")

    model = update_model(session=session, db_model=model, model_in=model_in)
    return model


@router.delete("/{llm_id}/models/{model_id}")
def delete_llm_model(
    llm_id: uuid.UUID,
    model_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """删除模型"""
    # 检查权限
    llm_config = get_llm_config_by_id(session=session, llm_id=llm_id)
    if not llm_config or llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此模型"
        )

    from app.db.repository import get_model_by_id

    model = get_model_by_id(session=session, model_id=model_id)
    if not model or model.llm_id != llm_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")

    success = delete_model(session=session, model_id=model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除模型失败"
        )

    return {"message": "模型删除成功"}
