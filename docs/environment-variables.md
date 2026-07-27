# 环境变量说明

本文档说明项目环境变量的用途、当前开发阶段的建议值及安全要求。

`.env.example` 是可提交到 Git 的配置模板，只保存变量名和无敏感性的示例值；`.env` 是每位成员自己的本地配置，不得提交到 Git。当前后端尚未完成初始化，因此本文档同时作为 4B02 阶段的配置约定。后续实现配置读取代码时，应以本文档和 `.env.example` 为准并同步更新。

## 一、快速开始

在项目根目录执行：

```powershell
Copy-Item .env.example .env
```

随后只修改 `.env` 中的本地真实值。至少应替换 `SECRET_KEY`；数据库和 MaxKB 相关配置可在对应服务准备完成后再填写。

可使用以下命令生成本地随机密钥：

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

将命令输出写入 `.env` 的 `SECRET_KEY`。不同开发成员可以使用不同密钥，不需要在群聊或仓库中共享。

## 二、变量总览

### 2.1 应用基础配置

| 变量 | 用途 | 本地开发建议 | 当前是否需要配置 | 是否敏感 |
|---|---|---|---|---|
| `APP_NAME` | 应用名称，可用于 API 文档标题、日志和服务标识 | `llm-ideological-case-platform` | 是，通常无需修改 | 否 |
| `APP_ENV` | 标识当前运行环境，供配置分支和日志使用 | `development` | 是 | 否 |
| `APP_HOST` | 后端监听地址 | `0.0.0.0` | 是，通常无需修改 | 否 |
| `APP_PORT` | 后端监听端口 | `8000` | 是；端口冲突时可修改 | 否 |
| `APP_DEBUG` | 是否启用开发调试行为 | `true` | 是 | 否 |
| `API_V1_PREFIX` | 第一版业务 API 的统一路径前缀 | `/api/v1` | 是，通常无需修改 | 否 |
| `LOG_LEVEL` | 最低日志级别 | `INFO` | 是 | 否 |

注意：

- `APP_ENV=development` 和 `APP_DEBUG=true` 仅适合本地开发，测试或生产环境不得直接照搬。
- `APP_HOST=0.0.0.0` 表示监听本机所有网络接口，便于容器和局域网联调；它不是浏览器访问地址。通常仍通过 `http://localhost:8000` 访问本机服务。
- 常见日志级别包括 `DEBUG`、`INFO`、`WARNING`、`ERROR`。日常开发优先使用 `INFO`，排查问题时可临时改为 `DEBUG`。

### 2.2 数据库配置

| 变量 | 用途 | 本地开发建议 | 当前是否需要配置 | 是否敏感 |
|---|---|---|---|---|
| `DATABASE_URL` | FastAPI 后端连接业务 PostgreSQL 数据库所需的完整地址 | 按本机 PostgreSQL 的账号、密码、端口和数据库名填写 | PostgreSQL 启用后必填 | 是 |

当前连接地址采用以下格式：

```text
postgresql+asyncpg://用户名:密码@主机:端口/数据库名
```

例如 `.env.example` 中的地址表示：

- 驱动：`asyncpg`；
- 用户名：`postgres`；
- 主机：`localhost`；
- 端口：`5432`；
- 数据库名：`ideological_case_platform`。

模板中的密码只是示例。实际数据库密码只能写入 `.env` 或部署平台的密钥管理系统，不得写入 `.env.example`、README、截图、聊天记录或代码。

如果密码包含 `@`、`:`、`/`、`#` 等特殊字符，需要进行 URL 编码，否则连接地址可能被错误解析。

### 2.3 跨域配置

| 变量 | 用途 | 本地开发建议 | 当前是否需要配置 | 是否敏感 |
|---|---|---|---|---|
| `CORS_ORIGINS` | 指定允许调用后端 API 的前端来源 | `http://localhost:5173` | 是，前后端联调时生效 | 否 |

`http://localhost:5173` 是常见的 Vite 本地开发地址。前端最终端口确定后，应与实际地址保持一致。

来源由协议、主机名和端口共同决定。例如，以下地址会被视为不同来源：

```text
http://localhost:5173
http://127.0.0.1:5173
http://localhost:3000
```

多个来源的表示格式将在 4B03 后端配置模型实现时固定。在此之前不要自行约定逗号、JSON 数组或其他格式，以免团队成员配置不一致。生产环境不得为方便而允许任意来源。

### 2.4 认证配置

| 变量 | 用途 | 本地开发建议 | 当前是否需要配置 | 是否敏感 |
|---|---|---|---|---|
| `SECRET_KEY` | 对登录令牌等安全数据进行签名 | 使用随机生成的高强度字符串 | 是，必须替换模板占位值 | 是 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 登录访问令牌的有效时长，单位为分钟 | `120` | 是，通常无需修改 | 否 |

`SECRET_KEY` 不是 MaxKB API Key，也不是数据库密码。更换它后，使用旧密钥签发的登录令牌将无法继续通过验证。生产环境必须生成独立密钥，不能复用任何成员的本地密钥。

### 2.5 MaxKB 服务配置

| 变量 | 用途 | 本地开发建议 | 当前是否需要配置 | 是否敏感 |
|---|---|---|---|---|
| `MAXKB_BASE_URL` | MaxKB 服务的基础访问地址 | 按实际地址填写，如 `http://localhost:8080` | 使用真实 MaxKB 时必填 | 通常否 |
| `MAXKB_API_KEY` | 后端调用 MaxKB API 时使用的凭据 | 从 MaxKB 中获取真实密钥 | 使用真实 MaxKB 时必填 | 是 |
| `MAXKB_TIMEOUT_SECONDS` | 后端等待 MaxKB 请求完成的最长时间，单位为秒 | `60` | 是，通常无需修改 | 否 |
| `MAXKB_MOCK_ENABLED` | 是否使用模拟响应代替真实 MaxKB 调用 | MaxKB 尚未联调时设为 `true` | 是 | 否 |

开发阶段建议保持：

```dotenv
MAXKB_MOCK_ENABLED=true
```

这样后端骨架和前端可以先围绕稳定的模拟契约开发。准备真实联调时，再确保地址、API Key 和应用标识均已配置，然后将其改为：

```dotenv
MAXKB_MOCK_ENABLED=false
```

`MAXKB_BASE_URL` 本身通常不是秘密，但如果其中包含内网域名、用户名、密码或访问令牌，也应按敏感信息处理。`MAXKB_API_KEY` 必须始终保存在服务端，不能下发给浏览器或写入前端环境变量。

### 2.6 MaxKB 应用标识

| 变量 | 对应能力 | 当前是否需要配置 | 是否敏感 |
|---|---|---|---|
| `MAXKB_QA_APPLICATION_ID` | 知识问答或案例检索问答应用 | 对应 MaxKB 应用发布后填写 | 通常否 |
| `MAXKB_GENERATION_APPLICATION_ID` | 案例辅助生成应用或工作流 | 对应 MaxKB 应用发布后填写 | 通常否 |
| `MAXKB_EVALUATION_APPLICATION_ID` | 案例智能评价应用或工作流 | 对应 MaxKB 应用发布后填写 | 通常否 |

这三个变量用于把业务功能映射到不同的 MaxKB 应用，不应互相混用。应用标识尚未确定时可以留空，但在真实调用模式下，调用某项能力前必须存在对应标识。

## 三、当前阶段推荐配置

4B02 至 4B03 初期可以按以下原则配置：

| 配置项 | 当前处理方式 |
|---|---|
| 应用基础配置 | 保持 `.env.example` 的默认值 |
| `DATABASE_URL` | PostgreSQL 已创建时填写真实本地连接地址；否则暂时保留示例，启动数据库前必须修改 |
| `CORS_ORIGINS` | 暂时保留 `http://localhost:5173`，待前端技术方案和端口确定后复核 |
| `SECRET_KEY` | 立即替换为本机随机值 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 暂时保留 `120` |
| `MAXKB_BASE_URL` | 有可访问的 MaxKB 实例时填写真实地址 |
| `MAXKB_API_KEY` | 尚未取得时保留占位值，但不得在真实调用模式下启动 |
| `MAXKB_MOCK_ENABLED` | 保持 `true` |
| 三个 MaxKB 应用标识 | 工作流发布前留空 |

## 四、配置安全规则

1. 真实密钥、密码和 Token 只写入 `.env` 或部署平台的密钥管理系统。
2. `.env.example` 必须保留可运行方向明确的示例，但不得包含任何真实凭据。
3. 后端日志不得输出 `DATABASE_URL`、`SECRET_KEY`、`MAXKB_API_KEY` 的完整内容。
4. 前端代码和前端构建变量中不得保存 `SECRET_KEY`、`MAXKB_API_KEY` 或数据库连接地址。
5. 如果敏感值曾被提交到 Git，仅删除文件或提交记录中的文本并不等于安全；必须立即作废并重新生成该凭据。
6. 不同环境应使用独立凭据，开发、测试和生产环境不得共用 `SECRET_KEY`、数据库密码或 MaxKB API Key。
7. 新增、重命名或删除环境变量时，应在同一个 Pull Request 中同步修改 `.env.example`、本文档和后端配置模型。

## 五、提交前自检

确认 `.env` 已被 Git 忽略：

```powershell
git check-ignore -v .env
```

检查工作区时，输出中不应出现 `.env`：

```powershell
git status --short
```

只比较 `.env` 和 `.env.example` 的变量名、避免输出真实值，可使用：

```powershell
$exampleNames = Get-Content .env.example |
    Where-Object { $_ -match '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=' } |
    ForEach-Object { ($_ -split '=', 2)[0].Trim() }

$localNames = Get-Content .env |
    Where-Object { $_ -match '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=' } |
    ForEach-Object { ($_ -split '=', 2)[0].Trim() }

Compare-Object $exampleNames $localNames
```

没有输出表示两份文件的变量名一致。该检查只验证变量是否存在，不验证值是否正确，也不会连接数据库或 MaxKB。
