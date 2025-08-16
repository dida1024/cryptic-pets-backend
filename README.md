# Cryptic Pets Backend

神秘宠物后端服务 - 基于 FastAPI 的现代化后端应用

## 项目简介

Cryptic Pets Backend 是一个采用领域驱动设计（DDD）架构的 FastAPI 后端服务，为神秘宠物平台提供强大的 API 支持。

## 技术栈

- **Web框架**: FastAPI
- **数据库**: PostgreSQL
- **ORM**: SQLModel
- **数据验证**: Pydantic
- **日志**: Loguru
- **认证**: JWT
- **容器化**: Docker & Docker Compose
- **监控**: Sentry
- **密码加密**: bcrypt
- **第三方集成**: OpenAI, Telegram Bot

## 项目特性

- 🏗️ **DDD架构**: 清晰的领域驱动设计分层架构
- 🚀 **高性能**: 基于FastAPI的异步性能
- 🔐 **安全认证**: JWT令牌认证机制
- 📊 **数据验证**: Pydantic强类型数据验证
- 🗄️ **数据库管理**: SQLModel ORM + PostgreSQL
- 📝 **结构化日志**: Loguru结构化日志记录
- 🐳 **容器化部署**: Docker容器化支持
- 🔍 **错误监控**: Sentry错误跟踪
- 🌐 **CORS支持**: 跨域资源共享配置
- 📧 **邮件服务**: 邮件通知功能

## 项目结构

```
cryptic-pets-backend/
├── application/           # 应用层
│   └── users/            # 用户应用服务
├── domain/               # 领域层
│   ├── base_entity.py    # 基础实体类
│   └── users/           # 用户领域模型
├── infrastructure/       # 基础设施层
│   ├── config.py        # 配置管理
│   ├── logging/         # 日志配置
│   └── persistence/     # 数据持久化
├── interfaces/          # 接口层
│   └── http/           # HTTP接口
└── docs/               # 项目文档
```

## 快速开始

### 环境要求

- Python 3.12+
- PostgreSQL 15+
- Redis 7.0+
- Docker & Docker Compose

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd cryptic-pets-backend
```

2. **安装依赖**
```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

3. **环境配置**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和其他环境变量
```

4. **启动数据库**
```bash
docker-compose up -d postgres redis
```

5. **运行应用**
```bash
# 开发模式
uvicorn main:app --reload

# 或使用 VS Code 调试器
```

### Docker 部署

```bash
docker-compose up -d
```

## API 文档

启动应用后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

## 环境变量配置

创建 `.env` 文件并配置以下变量：

```env
# 项目配置
PROJECT_NAME=Cryptic Pets Backend
ROOTPATH=/
ENVIRONMENT=local

# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=cryptic_pets

# Redis 配置
REDIS_PORT=6379

# 安全配置
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS 配置
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
FRONTEND_HOST=http://localhost:5173

# 邮件配置 (可选)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
EMAILS_FROM_EMAIL=your_email@gmail.com

# 第三方服务 (可选)
SENTRY_DSN=your_sentry_dsn
DEEPSEEK_API=your_deepseek_api_key
TELEGRAM_BOT_ROAD_TOKEN=your_telegram_token
```

## 开发指南

- [架构设计](docs/architecture.md) - 详细的架构设计说明
- [部署指南](docs/deployment.md) - 生产环境部署指南
- [开发指南](docs/development.md) - 开发规范和指南

## 代码质量

项目使用以下工具确保代码质量：

- **Ruff**: 代码格式化和静态分析
- **MyPy**: 类型检查
- **Pre-commit**: Git提交钩子
- **Pytest**: 单元测试

```bash
# 代码检查
ruff check .

# 类型检查
mypy .

# 运行测试
pytest
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issues: [GitHub Issues](../../issues)
- 邮箱: your_email@example.com

---

感谢使用 Cryptic Pets Backend! 🐾
