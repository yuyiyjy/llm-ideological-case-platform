"""FastAPI 应用级资源生命周期。"""

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from app.db.session import DatabaseManager
from app.integrations.maxkb.base import MaxKBAdapter

logger = logging.getLogger(__name__)

AppLifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_lifespan(
    database_manager: DatabaseManager,
    maxkb_adapter: MaxKBAdapter,
) -> AppLifespan:
    """为指定数据库资源管理器创建应用生命周期。

    使用工厂函数而不是模块级全局对象，可以让每个应用实例拥有独立引擎，
    并允许测试应用注入自己的数据库配置。数据库连接池和 MaxKB 适配器
    都由应用工厂创建，再在同一生命周期中按明确顺序释放。
    """

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # 此处只表示 SQLAlchemy 引擎对象已经准备好，不执行 SELECT 1，
        # 因而 PostgreSQL 暂时不可用时仍不影响非数据库接口启动。
        logger.info("数据库资源管理器已初始化，等待首次数据库操作")
        # HTTP 模式在应用构造时只创建 HTTPX 客户端对象，不会在启动阶段
        # 请求真实 MaxKB。日志只记录模式，不记录基础地址或 API Key。
        logger.info("MaxKB 适配器已初始化 mode=%s", maxkb_adapter.mode)
        try:
            yield
        finally:
            # 按资源创建的逆序先关闭外部 HTTP 客户端，再释放数据库连接池。
            # 即使 MaxKB 资源关闭失败，finally 仍保证数据库连接得到释放。
            try:
                await maxkb_adapter.aclose()
                logger.info("MaxKB 适配器已关闭 mode=%s", maxkb_adapter.mode)
            finally:
                # dispose() 会关闭连接池中的连接。即使启动期间从未访问数据库，
                # 调用它也保持幂等和安全，确保测试及热重载不会遗留资源。
                await database_manager.dispose()
                logger.info("数据库连接池已释放")

    return lifespan
