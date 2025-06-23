from fastapi import APIRouter

from app.api.v1.endpoints import (
    agents,
    chat,
    conversations,
    dashboard,
    llm_configs,
    login,
    messages,
    models,
    users,
    utils,
    websocket_chat,
)

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(
    llm_configs.router, prefix="/llm-configs", tags=["llm-configs"]
)
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(
    conversations.router, prefix="/conversations", tags=["conversations"]
)
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(websocket_chat.router, prefix="/ws", tags=["websocket"])
