# 基础设施与部署

本目录保存项目运行和交付所需的基础设施配置。

## 内容范围

- Dockerfile 和 Docker Compose；
- PostgreSQL 业务数据库配置；
- MaxKB 独立服务的镜像版本和接入说明；
- Nginx、端口、域名、HTTPS 和跨域配置；
- 健康检查、日志和故障排查说明；
- 备份、恢复、发布和回退流程。

## 边界

- 仓库只保存配置模板和可复现说明；
- 不保存 Docker Volume、数据库文件、上传文件或备份数据；
- 不在配置文件中写入真实密码和 API Key；
- MaxKB 使用固定镜像版本独立部署，不复制其完整源码；
- 本地、共享测试和正式部署环境应使用不同配置。

## 当前状态

`compose.yaml` 已提供 4B03 本地开发所需的 PostgreSQL 17 服务：

- 仅绑定本机 `127.0.0.1:5433`；
- 使用 Docker 命名卷持久化数据；
- 使用根目录 `.env` 提供初始化变量；
- 提供 PostgreSQL 就绪健康检查；
- 不包含 MaxKB，也不访问 MaxKB 内部数据库。

当前 Compose 配置只服务于本地业务后端开发。后端依赖安装、数据库启动、Alembic 迁移和 FastAPI 启动命令见 `backend/README.md`。后续生产部署、Nginx 和 MaxKB 独立部署方案仍需单独设计和审查。
