from fastapi import APIRouter

from app.api.v1.endpoints import items, login, users, utils

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(utils.router)
