"""FastAPI 应用级资源生命周期。"""

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from app.db.session import DatabaseManager

logger = logging.getLogger(__name__)

AppLifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_lifespan(database_manager: DatabaseManager) -> AppLifespan:
    """为指定数据库资源管理器创建应用生命周期。

    使用工厂函数而不是模块级全局对象，可以让每个应用实例拥有独立引擎，
    并允许测试应用注入自己的数据库配置。后续接入 MaxKB HTTP 客户端时，
    也可以在同一生命周期中统一管理其关闭顺序。
    """

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # 此处只表示 SQLAlchemy 引擎对象已经准备好，不执行 SELECT 1，
        # 因而 PostgreSQL 暂时不可用时仍不影响非数据库接口启动。
        logger.info("数据库资源管理器已初始化，等待首次数据库操作")
        try:
            yield
        finally:
            # dispose() 会关闭连接池中的连接。即使启动期间从未访问数据库，
            # 调用它也保持幂等和安全，确保测试及热重载不会遗留资源。
            await database_manager.dispose()
            logger.info("数据库连接池已释放")

    return lifespan
