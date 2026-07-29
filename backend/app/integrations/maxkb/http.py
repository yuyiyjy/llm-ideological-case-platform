"""基于 HTTPX 的 MaxKB HTTP 适配器骨架。"""

from typing import ClassVar

import httpx
from pydantic import SecretStr

from app.integrations.maxkb.base import MaxKBAdapter, MaxKBAdapterMode


class HttpMaxKBAdapter(MaxKBAdapter):
    """持有真实 MaxKB HTTP 连接资源的适配器骨架。

    构造函数只创建 HTTPX 异步客户端，不会建立网络连接或发送请求。
    4B03 不假设 MaxKB 的接口路径、认证头和业务载荷；这些内容必须等
    已发布应用的 API 契约确认后，封装为适配器内部的业务语义方法。

    API Key 使用 SecretStr 保存，不放入对象 repr、日志或应用响应。
    HTTPX 客户端保持私有，防止路由和业务服务绕过适配层直接调用 MaxKB。
    """

    _mode: ClassVar[MaxKBAdapterMode] = "http"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: SecretStr,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        # 只在适配器内部保留 SecretStr。后续实现具体请求时，应在发送前
        # 临时读取明文并按已确认的 MaxKB 认证规范构造请求头。
        self._api_key = api_key

        # 统一补充末尾斜杠，使后续相对路径解析始终以配置的基础路径为根。
        # follow_redirects 固定关闭，避免凭据在未经审查的跨域重定向中传播。
        normalized_base_url = f"{base_url.rstrip('/')}/"
        self._client = httpx.AsyncClient(
            base_url=normalized_base_url,
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=False,
            transport=transport,
        )

    @property
    def mode(self) -> MaxKBAdapterMode:
        """返回 HTTP 运行模式。"""
        return self._mode

    @property
    def is_closed(self) -> bool:
        """返回底层 HTTPX 客户端是否已经关闭。"""
        return self._client.is_closed

    async def aclose(self) -> None:
        """关闭底层 HTTPX 异步客户端及其连接池。"""
        await self._client.aclose()

    def __repr__(self) -> str:
        """返回不包含基础地址、API Key 和请求头的安全表示。"""
        return f"{type(self).__name__}(mode={self.mode!r}, closed={self.is_closed!r})"
