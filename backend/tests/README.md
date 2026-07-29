# 后端测试

测试按依赖范围分为：

```text
api/          FastAPI 路由、接口文档和异常响应
unit/         配置、数据库基础设施和 MaxKB 适配层
integration/  需要本地 PostgreSQL 等外部服务的集成检查
```

默认测试使用完整的合成配置，不读取根目录 `.env` 中的真实值，也不会连接 PostgreSQL 或请求 MaxKB：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

仅在本地 Docker PostgreSQL 已启动并完成迁移后，显式运行集成测试：

```powershell
.\.venv\Scripts\python.exe -m pytest --run-integration
```

`--run-integration` 会允许标记为 `integration` 的测试读取本地 `.env` 并连接业务数据库，但仍不会请求真实 MaxKB。测试日志、失败信息和断言不得输出数据库密码、API Key 或完整连接地址。
