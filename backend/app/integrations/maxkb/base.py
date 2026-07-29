"""MaxKB 适配器抽象接口。"""

from abc import ABC, abstractmethod
from typing import Literal

MaxKBAdapterMode = Literal["mock", "http"]


class MaxKBAdapter(ABC):
    """所有 MaxKB 实现必须遵循的最小生命周期接口。

    4B03 只确定适配层边界、运行模式和资源释放方式，不提前确定问答、
    生成、评价等业务能力的请求与响应结构。后续确认 MaxKB 已发布应用
    的 HTTP 契约后，再在该抽象层增加面向业务语义的方法。

    业务服务只能依赖本抽象接口，不能直接取得 HTTPX 客户端，更不能
    导入 MaxKB 源码或连接 MaxKB 内部数据库。
    """

    @property
    @abstractmethod
    def mode(self) -> MaxKBAdapterMode:
        """返回当前适配器运行模式。"""

    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """返回适配器持有的资源是否已经关闭。"""

    @abstractmethod
    async def aclose(self) -> None:
        """释放适配器持有的异步资源。"""
