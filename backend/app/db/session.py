from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager

from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[Session, None]:
    """异步上下文管理器，用于在WebSocket或其他异步环境中管理数据库会话"""
    with Session(engine) as session:
        yield session
