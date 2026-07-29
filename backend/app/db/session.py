"""异步数据库引擎、会话工厂和 FastAPI 会话依赖。"""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseManager:
    """集中持有业务数据库的异步引擎和会话工厂。

    每个 FastAPI 应用实例拥有一个 DatabaseManager。应用启动时只创建
    SQLAlchemy 引擎对象，不会立即建立 PostgreSQL 网络连接；第一次执行
    SQL 语句时，SQLAlchemy 才会从连接池获取实际连接。
    """

    def __init__(self, database_url: str) -> None:
        # pool_pre_ping 会在复用已有连接前检查连接是否仍然有效，能够减少
        # PostgreSQL 重启或网络短暂中断后取到失效连接的概率。
        # echo 固定关闭，避免 SQL 参数中的业务数据或敏感内容进入日志。
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            echo=False,
        )

        # expire_on_commit=False 允许业务代码在提交后继续读取已加载属性，
        # 避免异步环境下因自动过期而触发不可控的隐式查询。
        # autoflush=False 要求业务代码明确 flush 或 commit，使写入时机可审查。
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def dispose(self) -> None:
        """关闭连接池并释放当前应用持有的全部数据库连接。"""
        await self.engine.dispose()


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """为单次 HTTP 请求提供独立的异步数据库会话。

    该依赖不会自动提交事务。新增、修改或删除数据的业务服务必须在完整
    业务操作成功后显式调用 ``commit()``；若请求处理抛出异常，则依赖会
    回滚当前事务。离开依赖作用域后，会话始终关闭并归还底层连接。
    """
    database_manager = getattr(request.app.state, "database", None)
    if not isinstance(database_manager, DatabaseManager):
        # 只有应用生命周期配置错误时才会进入此分支。这里不回退到全局
        # 引擎，以免测试或多应用进程意外共享错误的连接池。
        raise RuntimeError("数据库资源尚未初始化")

    async with database_manager.session_factory() as session:
        try:
            yield session
        except Exception:
            # rollback() 在尚未开启事务时也是安全操作，因此无需让调用方
            # 判断当前事务状态。回滚完成后继续抛出原异常交给全局处理器。
            await session.rollback()
            raise
