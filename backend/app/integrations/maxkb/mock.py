"""不产生外部网络请求的 MaxKB Mock 适配器。"""

from typing import ClassVar

from app.integrations.maxkb.base import MaxKBAdapter, MaxKBAdapterMode


class MockMaxKBAdapter(MaxKBAdapter):
    """开发和测试阶段使用的 MaxKB Mock 实现。

    当前骨架不伪造问答、生成或评价结果，以免在真实工作流契约尚未确认
    时形成错误的共享字段。后续每增加一项业务能力，应同时为本实现增加
    可预测的模拟响应，并由契约测试保证 Mock 与 HTTP 实现语义一致。
    """

    _mode: ClassVar[MaxKBAdapterMode] = "mock"

    def __init__(self) -> None:
        self._is_closed = False

    @property
    def mode(self) -> MaxKBAdapterMode:
        """返回 Mock 运行模式。"""
        return self._mode

    @property
    def is_closed(self) -> bool:
        """返回 Mock 适配器是否已经关闭。"""
        return self._is_closed

    async def aclose(self) -> None:
        """关闭 Mock 适配器。

        Mock 当前没有网络资源，但仍实现统一关闭接口。这样应用生命周期
        无需判断具体类型，后续 Mock 增加队列或异步资源时也不必修改调用方。
        """
        self._is_closed = True
