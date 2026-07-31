# 启动与基础检查流程

> 对应任务：4B05
> 当前版本：阶段版
> 适用环境：Windows PowerShell、本地开发

本文档是当前项目本地启动顺序和基础检查清单的统一入口。后端实现细节以
[`backend/README.md`](../backend/README.md) 为准，环境变量含义以
[`environment-variables.md`](environment-variables.md) 为准。

当前阶段已经具备 PostgreSQL、Alembic、FastAPI 和 MaxKB Mock 模式的启动条件。
前端工程尚未初始化，真实 MaxKB 业务调用也尚未实现，因此本文档不会把前端启动、
真实 MaxKB 联调或完整系统联调描述成已完成功能。

## 一、当前可启动范围

当前可以启动和检查：

- Docker Compose 中的 PostgreSQL 17 业务数据库；
- FastAPI 业务后端；
- Alembic 数据库迁移；
- 健康检查、Swagger UI、ReDoc 和 OpenAPI；
- 不产生外部网络请求的 MaxKB Mock 适配器；
- 后端离线测试和显式启用的 PostgreSQL 集成测试。

当前不能完整启动或验证：

- 前端：任务 3 尚未完成工程初始化和技术选型；
- 真实 MaxKB 业务调用：HTTP 适配器尚未实现认证头、接口路径和业务方法；
- 核心业务表：4B04 尚未形成业务模型和迁移；
- 完整前后端、数据库和 MaxKB 联调。

## 二、启动顺序

当前推荐顺序如下：

```text
检查开发工具
  ↓
准备根目录 .env
  ↓
准备后端虚拟环境和依赖
  ↓
启动 PostgreSQL
  ↓
等待 PostgreSQL 健康
  ↓
执行 Alembic 迁移
  ↓
启动 FastAPI
  ↓
检查健康接口和 API 文档
  ↓
运行后端测试
```

前端加入项目后，应在 FastAPI 检查通过之后启动前端。真实 MaxKB 加入联调后，
应作为独立服务先确认可用，再把后端从 Mock 模式切换到 HTTP 模式。

## 三、首次环境准备

以下命令均从项目根目录开始执行。

### 3.1 检查开发工具

```powershell
py -3.13 --version
docker --version
docker compose version
git status --short --branch
```

基础要求：

- Python 必须满足 `>=3.13,<3.14`；
- Docker 命令和 Docker Compose 插件必须可用；
- 执行容器命令前，Docker Desktop 或其他 Docker 服务必须已经启动；
- 应在当前任务分支中工作，不直接修改 `main`。

只检查 Compose 文件和可提交配置模板的语法时，可以执行：

```powershell
docker compose --env-file .env.example -f infra/compose.yaml config --quiet
```

该命令不会启动容器。`.env.example` 只用于模板和静态检查，不得作为真实环境配置。

### 3.2 准备本地环境变量

仅在根目录不存在 `.env` 时复制模板：

```powershell
if (-not (Test-Path -LiteralPath .env)) {
    Copy-Item -LiteralPath .env.example -Destination .env
}
```

随后在本地 `.env` 中至少完成以下配置：

- 将 `SECRET_KEY` 替换为不少于 32 个字符的随机值；
- 将 `POSTGRES_PASSWORD` 替换为本地数据库密码；
- 确保 `POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_DB` 与
  `DATABASE_URL` 中的账号、密码和数据库名一致；
- 本地 Docker 数据库的 `DATABASE_URL` 使用端口 `5433`；
- 当前阶段保持 `MAXKB_MOCK_ENABLED=true`。

确认 `.env` 已被 Git 忽略：

```powershell
git check-ignore -v .env
```

该命令应显示 `.gitignore` 中匹配 `.env` 的规则。不得把 `.env` 内容、数据库连接地址、
密码、Secret 或 API Key 输出到日志、截图、提交或聊天记录。

### 3.3 创建后端虚拟环境

首次准备后端环境时执行：

```powershell
Set-Location backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
Set-Location ..
```

后续启动和测试统一使用 `backend/.venv`，不依赖系统默认 Python。

## 四、启动 PostgreSQL

确认 Docker 服务已经运行，然后在项目根目录执行：

```powershell
docker compose --env-file .env -f infra/compose.yaml up -d postgres
docker compose --env-file .env -f infra/compose.yaml ps postgres
```

预期结果：

- 服务名为 `postgres`；
- 容器处于运行状态；
- 健康状态最终变为 `healthy`；
- 本机地址为 `127.0.0.1:5433`；
- PostgreSQL 容器内部端口为 `5432`。

如果健康状态仍为 `starting`，等待几秒后重新执行 `ps`。如果状态为 `unhealthy`，
先查看非敏感状态和日志，不要通过删除命名卷的方式重新初始化：

```powershell
docker compose --env-file .env -f infra/compose.yaml ps postgres
docker compose --env-file .env -f infra/compose.yaml logs --tail 100 postgres
```

日志中不得复制或传播密码、Token、完整数据库连接地址或其他敏感信息。

## 五、执行数据库迁移

PostgreSQL 健康后执行：

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic heads
Set-Location ..
```

`current` 显示的数据库版本应与 `heads` 显示的代码迁移头一致。

当前代码只有 `20260728_0001` 空基线迁移，不会创建案例、用户、审核等业务表。
4B04 将来增加业务迁移后，启动流程仍然使用 `alembic upgrade head`，不需要在本文档中
固定具体业务迁移版本。

应用启动不会自动执行迁移。每次拉取包含新迁移的代码后，应在启动相关业务功能前
重新执行 `alembic upgrade head`。

## 六、启动 FastAPI

打开一个新的 PowerShell 窗口，进入项目根目录后执行：

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

当前命令使用 Uvicorn 的本地开发默认地址 `127.0.0.1:8000`。`--reload` 只适合开发环境，
不应用于测试服务器或生产部署。

启动时应注意：

- 配置校验失败会阻止应用启动；
- 创建 SQLAlchemy 引擎不会立即连接 PostgreSQL；
- Mock 模式不会创建 MaxKB HTTP 客户端，也不会请求真实 MaxKB；
- 健康检查只证明 FastAPI 进程能够响应，不代表 PostgreSQL 或 MaxKB 已通过检查。

## 七、基础检查

在另一个 PowerShell 窗口中执行以下检查。

### 7.1 健康检查

```powershell
$health = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"
$health.status
```

预期输出：

```text
ok
```

### 7.2 API 文档

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/docs").StatusCode
(Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/redoc").StatusCode
(Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/openapi.json").StatusCode
```

三个状态码都应为 `200`。

检查 OpenAPI 是否包含健康检查接口：

```powershell
$openApi = Invoke-RestMethod -Uri "http://localhost:8000/openapi.json"
$openApi.paths.PSObject.Properties.Name
```

输出路径中应包含：

```text
/api/v1/health
```

### 7.3 默认离线测试

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest
Set-Location ..
```

默认测试使用合成配置，不读取根目录 `.env` 中的真实值，不连接 PostgreSQL，
也不请求 MaxKB。当前预期结果为：

```text
19 passed, 1 skipped
```

跳过项是必须显式启用的 PostgreSQL 集成测试。

### 7.4 PostgreSQL 集成测试

只有在 PostgreSQL 健康且迁移已经执行后，才运行：

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest --run-integration -m integration
Set-Location ..
```

该测试会读取本地 `.env`，执行真实 `SELECT 1`，并检查数据库 Alembic 版本是否位于
代码迁移头。测试仍然不会请求真实 MaxKB。

## 八、当前阶段检查清单

| 检查项 | 通过标准 |
|---|---|
| Python 版本 | `3.13.x` |
| Docker CLI | 可以显示版本 |
| Docker 服务 | 可以连接 Docker API |
| Compose 配置 | `config --quiet` 无错误退出 |
| 本地配置 | `.env` 存在且被 Git 忽略 |
| MaxKB 模式 | 当前保持 Mock 模式 |
| PostgreSQL | 容器处于 `healthy` |
| 数据库迁移 | `alembic current` 与 `alembic heads` 一致 |
| FastAPI | Uvicorn 正常启动且没有配置校验错误 |
| 健康检查 | 返回 `{"status":"ok"}` |
| API 文档 | Swagger、ReDoc、OpenAPI 均返回 `200` |
| 默认测试 | 当前为 19 项通过、1 项跳过 |
| 集成测试 | 显式启用后 PostgreSQL 连接和迁移版本检查通过 |

## 九、停止服务

### 9.1 停止 FastAPI

在运行 Uvicorn 的窗口按 `Ctrl+C`，确认进程已经退出。

### 9.2 停止 PostgreSQL 并保留数据

在项目根目录执行：

```powershell
docker compose --env-file .env -f infra/compose.yaml stop postgres
docker compose --env-file .env -f infra/compose.yaml ps postgres
```

`stop` 会停止容器，但不会删除 PostgreSQL 命名卷。下次可以再次使用
`up -d postgres` 启动。

不要为了排查普通启动问题执行以下类型的操作：

```text
docker compose down --volumes
docker compose down -v
docker volume rm ...
```

这些操作可能删除数据库命名卷。删除、重建或清空数据库之前，必须先确认数据、
备份和对其他成员的影响。

## 十、常见问题

### 10.1 无法连接 Docker API

典型信息包括 `failed to connect to the docker API` 或找不到
`docker_engine`。先启动 Docker Desktop 或当前系统使用的 Docker 服务，再重新运行
`docker info` 和 Compose 命令。

### 10.2 PostgreSQL 端口被占用

Compose 固定绑定 `127.0.0.1:5433`。可以使用以下命令检查端口：

```powershell
Get-NetTCPConnection -LocalPort 5433 -ErrorAction SilentlyContinue
```

不要只修改 Compose 端口。端口发生变化时，还必须同步修改本地 `DATABASE_URL` 和相关文档。

### 10.3 FastAPI 端口被占用

检查本机 `8000` 端口：

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

如需临时使用其他端口，应在 Uvicorn 命令中显式添加 `--port`，并同步使用新的健康检查地址。

### 10.4 修改密码后数据库仍然认证失败

PostgreSQL 官方镜像只在命名卷为空时使用 `POSTGRES_*` 初始化账号和数据库。
已有命名卷不会因为修改 `.env` 自动更改内部账号或密码。此时应先确认现有数据和初始化历史，
不要直接删除命名卷。

### 10.5 Alembic 迁移失败

依次检查：

1. PostgreSQL 容器是否为 `healthy`；
2. `DATABASE_URL` 的账号、密码、端口和数据库名是否与容器初始化配置一致；
3. 当前工作目录是否为 `backend`；
4. 当前分支是否包含预期迁移；
5. `alembic current` 和 `alembic heads` 是否一致。

不得使用手工修改 `alembic_version` 表的方式绕过迁移问题。

### 10.6 健康检查通过但数据库不可用

这是当前设计的预期行为。`/api/v1/health` 只检查 Web 应用存活状态，不执行数据库查询，
也不探测 MaxKB。需要通过 PostgreSQL 容器状态、Alembic 命令和显式集成测试确认数据库。

## 十一、待后续补充

### 11.1 前端启动与联调

前端技术栈、依赖安装方式、开发端口和启动命令尚未确定。任务 3 完成工程初始化后，
需要补充：

- Node.js 和包管理器版本；
- 前端依赖安装与启动命令；
- 实际开发端口及 CORS 对齐；
- 前端基础页面检查；
- Mock API 和真实 API 的切换方法；
- 完整前后端联调顺序。

在这些信息确认前，不得根据常见 Vite 或其他框架习惯虚构启动命令。

### 11.2 真实 MaxKB 联调

当前 `infra/compose.yaml` 不部署 MaxKB，HTTP 适配器也不能执行真实业务调用。
后续完成 MaxKB 基线部署、工作流发布和 API 契约后，需要补充：

- MaxKB 独立服务的启动与健康检查；
- 固定版本或镜像标签；
- 应用 ID 和 API Key 的服务端配置；
- 后端从 Mock 模式切换到 HTTP 模式的条件；
- 问答、生成和评价的冒烟检查；
- 超时、空结果和服务不可用的回退验证。

### 11.3 部署环境

本文档只覆盖本地开发。学校服务器、云服务器、Nginx、HTTPS、备份、恢复和版本回退
属于后续部署任务，不能直接照搬本地开发配置。

