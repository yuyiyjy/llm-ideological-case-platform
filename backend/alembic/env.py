"""Alembic 迁移运行环境。

在线模式使用 SQLAlchemy 异步引擎连接 PostgreSQL；离线模式只生成 SQL，
不会建立网络连接。两种模式都从应用 Settings 读取同一个 DATABASE_URL，
避免应用和迁移工具各自维护数据库配置。
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings
from app.db.base import Base

config = context.config

# Alembic CLI 独立运行时使用 alembic.ini 中的日志配置。测试或其他工具
# 未提供配置文件名时跳过，避免 fileConfig 接收到空路径。
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4B04 新增业务模型后，需要确保模型模块在此文件执行前已被导入。
# 当前阶段没有业务模型，因此 metadata 为空，初始迁移不会创建任何业务表。
target_metadata = Base.metadata


def get_database_url() -> str:
    """从统一应用配置读取数据库地址，不在 Alembic 文件中保存凭据。"""
    return str(get_settings().database_url)


def run_migrations_offline() -> None:
    """在不连接 PostgreSQL 的情况下生成迁移 SQL。"""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    # 离线模式只把迁移操作编译为 SQL 文本，不会执行 SQL，也不会检查
    # PostgreSQL 是否正在运行，适合代码审查和 CI 中的静态迁移检查。
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_with_connection(connection: Connection) -> None:
    """在同步连接适配层中执行 Alembic 迁移。"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """创建一次性异步引擎并执行在线迁移。"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    # Alembic 命令是短生命周期进程，使用 NullPool 可以避免命令结束后
    # 保留无意义的连接池；业务应用仍使用自己的长期异步连接池。
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            # Alembic 内部迁移 API 仍是同步接口，run_sync 会在异步连接上
            # 安全执行同步迁移函数，而不是引入第二套同步 PostgreSQL 驱动。
            await connection.run_sync(run_migrations_with_connection)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """启动事件循环并执行在线异步迁移。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
