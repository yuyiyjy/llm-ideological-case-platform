"""SQLAlchemy 声明式模型基类。"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# 统一约束名称后，Alembic 生成的迁移不会依赖 PostgreSQL 临时分配的名称。
# 后续排查约束冲突或编写回滚迁移时，也能直接根据表名和字段名定位对象。
CONSTRAINT_NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """所有自研业务模型必须继承的声明式基类。

    这里只建立统一的 SQLAlchemy metadata，不包含任何业务字段或表。
    4B04 新增模型后，Alembic 会通过此 metadata 发现模型变更。
    """

    metadata = MetaData(naming_convention=CONSTRAINT_NAMING_CONVENTION)
