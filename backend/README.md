# 业务后端

本目录用于建设项目自研的课程思政业务后端。

## 主要职责

- 用户、角色和业务权限；
- 课程、知识点和思政标签管理；
- 案例创建、编辑、查询和筛选；
- 案例版本、审核、发布和归档；
- AI 生成、评价和问答任务编排；
- MaxKB 适配器与结构化输出校验；
- 统一异常、日志、配置和接口文档。

## 技术栈

```text
Python
FastAPI
Pydantic 2
pydantic-settings
SQLAlchemy 2
Alembic
PostgreSQL 17
asyncpg
HTTPX
Pytest
```

Python 版本范围和直接依赖的精确版本统一声明在 `pyproject.toml` 中。当前要求 Python `>=3.13,<3.14`。

## 边界

- 不直接修改或导入 MaxKB 的 Django 业务代码；
- 不直接读写 MaxKB 内部数据库；
- 不向前端暴露 MaxKB API Key；
- 通过独立适配器调用 MaxKB 已发布的应用接口；
- 即使 MaxKB 暂时不可用，非 AI 业务仍应能够正常运行。

## 本地启动

以下命令均在 Windows PowerShell 中执行。

### 1. 准备环境变量

在项目根目录复制配置模板，并按说明替换本地值：

```powershell
Copy-Item .env.example .env
```

`.env` 不得提交到 Git。数据库变量之间必须满足：

- `POSTGRES_USER` 与 `DATABASE_URL` 中的用户名一致；
- `POSTGRES_PASSWORD` 与 `DATABASE_URL` 中经过 URL 编码前的密码一致；
- `POSTGRES_DB` 与 `DATABASE_URL` 中的数据库名一致；
- Docker 本地数据库的 `DATABASE_URL` 端口使用 `5433`。

完整约定见根目录的 `docs/environment-variables.md`。

### 2. 启动 PostgreSQL

在项目根目录执行：

```powershell
docker compose --env-file .env -f infra/compose.yaml up -d postgres
docker compose --env-file .env -f infra/compose.yaml ps
```

Compose 使用 PostgreSQL 17，并将本机 `127.0.0.1:5433` 映射到容器内部 `5432`。数据库文件保存在 Docker 命名卷中，不会写入仓库。

### 3. 创建 Python 虚拟环境并安装依赖

进入 `backend` 目录：

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

仓库根目录不需要额外的 Python 虚拟环境；后端统一使用 `backend/.venv`。

### 4. 执行数据库迁移

仍在 `backend` 目录执行：

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

4B03 的初始迁移只建立 Alembic 版本基线，不创建案例、用户、审核等业务表。核心业务表将在 4B04 完成设计确认后通过新迁移创建。

### 5. 启动 FastAPI

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动后可访问：

- 健康检查：`http://localhost:8000/api/v1/health`
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- OpenAPI JSON：`http://localhost:8000/openapi.json`

健康检查只验证 Web 应用是否可以响应，不主动探测 PostgreSQL 或 MaxKB。

### 6. 停止本地数据库

回到项目根目录执行：

```powershell
docker compose --env-file .env -f infra/compose.yaml stop postgres
```

该命令不会删除命名卷。不要直接执行带 `--volumes` 或 `-v` 的删除命令；删除数据库命名卷前必须先确认数据和备份影响。

## 数据库基础设施边界

- FastAPI 和 Alembic 共享同一个 `DATABASE_URL`；
- SQLAlchemy 使用异步 `asyncpg` 驱动；
- 应用启动只初始化连接池，不主动连接数据库；
- 每个请求获得独立异步会话，写操作由业务服务显式提交；
- Alembic 当前只有空基线迁移，不包含核心业务表；
- PostgreSQL 业务数据库与 MaxKB 内部数据库完全独立。
