"""
模型管理API端点
处理用户的模型创建、查看、更新和删除
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.dependencies import get_current_user, SessionDep
from app.db.repository import (
    create_model,
    delete_model,
    get_llm_config_by_id,
    get_model_by_id,
    get_models_by_user,
    update_model,
)
from app.models import User
from app.schemas import (
    ModelCreate,
    ModelPublic,
    ModelsPublic,
    ModelUpdate,
)

router = APIRouter()


@router.get("/", response_model=ModelsPublic)
def get_user_models(
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> ModelsPublic:
    """获取当前用户的所有模型"""
    models = get_models_by_user(
        session=session, user_id=current_user.user_id, skip=skip, limit=limit
    )
    return ModelsPublic(data=models, count=len(models))


@router.post("/", response_model=ModelPublic)
def create_user_model(
    *,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    model_in: ModelCreate,
) -> ModelPublic:
    """创建新的模型配置"""
    # 验证 LLM 配置是否属于当前用户
    llm_config = get_llm_config_by_id(session=session, llm_id=model_in.llm_id)
    if not llm_config or llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM配置不存在或无权访问"
        )

    model = create_model(session=session, model_create=model_in)
    return model


@router.get("/{model_id}", response_model=ModelPublic)
def get_model(
    model_id: uuid.UUID,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ModelPublic:
    """获取指定模型的详细信息"""
    model = get_model_by_id(session=session, model_id=model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")

    # 验证权限：通过关联的 LLM 配置检查
    llm_config = get_llm_config_by_id(session=session, llm_id=model.llm_id)
    if not llm_config or llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此模型"
        )

    return model


@router.put("/{model_id}", response_model=ModelPublic)
def update_user_model(
    *,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
    model_id: uuid.UUID,
    model_in: ModelUpdate,
) -> ModelPublic:
    """更新模型配置"""
    model = get_model_by_id(session=session, model_id=model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")

    # 验证权限
    llm_config = get_llm_config_by_id(session=session, llm_id=model.llm_id)
    if not llm_config or llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此模型"
        )

    model = update_model(session=session, db_model=model, model_in=model_in)
    return model


@router.delete("/{model_id}")
def delete_user_model(
    model_id: uuid.UUID,
    session: Annotated[Session, Depends(SessionDep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """删除模型配置"""
    model = get_model_by_id(session=session, model_id=model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")

    # 验证权限
    llm_config = get_llm_config_by_id(session=session, llm_id=model.llm_id)
    if not llm_config or llm_config.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此模型"
        )

    success = delete_model(session=session, model_id=model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除模型失败"
        )

    return {"message": "模型删除成功"}
