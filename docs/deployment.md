# 部署指南

## 概述

本文档详细介绍如何在不同环境中部署 Cryptic Pets Backend 应用程序。支持本地开发、测试环境和生产环境的部署方案。

## 环境要求

### 系统要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+) / macOS / Windows
- **Python**: 3.12+
- **内存**: 最少 2GB，推荐 4GB+
- **存储**: 最少 10GB 可用空间

### 依赖服务
- **PostgreSQL**: 15.3+
- **Redis**: 7.0+
- **Docker**: 20.10+ (可选)
- **Docker Compose**: 2.0+ (可选)

## 部署方式

### 1. Docker 部署 (推荐)

#### 1.1 准备环境文件

创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
# 项目配置
PROJECT_NAME=Cryptic Pets Backend
ROOTPATH=/
ENVIRONMENT=production

# 数据库配置
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_USER=cryptic_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=cryptic_pets

# Redis 配置
REDIS_PORT=6379

# 安全配置
SECRET_KEY=your_super_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS 配置
BACKEND_CORS_ORIGINS=https://your-frontend-domain.com
FRONTEND_HOST=https://your-frontend-domain.com

# 监控配置
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=your_email@gmail.com
```

#### 1.2 构建和启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

#### 1.3 验证部署

```bash
# 检查应用健康状态
curl http://localhost:8000/docs

# 检查数据库连接
docker-compose exec app python -c "from infrastructure.persistence.postgres.init_db import init_db; init_db()"
```

### 2. 传统部署

#### 2.1 系统依赖安装

**Ubuntu/Debian:**
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.12
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# 安装其他依赖
sudo apt install build-essential libpq-dev nginx supervisor -y
```

**CentOS/RHEL:**
```bash
# 安装 EPEL 仓库
sudo yum install epel-release -y

# 安装 Python 3.12
sudo yum install python3.12 python3.12-devel gcc postgresql-devel -y

# 安装其他依赖
sudo yum install nginx supervisor -y
```

#### 2.2 PostgreSQL 安装配置

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib -y

# CentOS/RHEL  
sudo yum install postgresql postgresql-server postgresql-contrib -y
sudo postgresql-setup initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
```

在 PostgreSQL 中执行：
```sql
CREATE USER cryptic_user WITH PASSWORD 'secure_password_123';
CREATE DATABASE cryptic_pets OWNER cryptic_user;
GRANT ALL PRIVILEGES ON DATABASE cryptic_pets TO cryptic_user;
\q
```

#### 2.3 Redis 安装配置

```bash
# Ubuntu/Debian
sudo apt install redis-server -y

# CentOS/RHEL
sudo yum install redis -y

# 启动服务
sudo systemctl start redis
sudo systemctl enable redis
```

#### 2.4 应用部署

```bash
# 创建应用目录
sudo mkdir -p /opt/cryptic-pets-backend
sudo chown $USER:$USER /opt/cryptic-pets-backend
cd /opt/cryptic-pets-backend

# 克隆代码
git clone <repository-url> .

# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate

# 安装依赖
pip install uv
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 初始化数据库
python -c "from infrastructure.persistence.postgres.init_db import init_db; init_db()"
```

#### 2.5 Systemd 服务配置

创建服务文件 `/etc/systemd/system/cryptic-pets.service`：

```ini
[Unit]
Description=Cryptic Pets Backend
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/cryptic-pets-backend
Environment=PATH=/opt/cryptic-pets-backend/venv/bin
ExecStart=/opt/cryptic-pets-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start cryptic-pets
sudo systemctl enable cryptic-pets
sudo systemctl status cryptic-pets
```

#### 2.6 Nginx 反向代理配置

创建 Nginx 配置文件 `/etc/nginx/sites-available/cryptic-pets`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书配置
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 日志配置
    access_log /var/log/nginx/cryptic-pets.access.log;
    error_log /var/log/nginx/cryptic-pets.error.log;

    # 代理配置
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件处理
    location /static {
        alias /opt/cryptic-pets-backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/cryptic-pets /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Kubernetes 部署

#### 3.1 准备 Kubernetes 配置

创建命名空间：
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cryptic-pets
```

#### 3.2 ConfigMap 和 Secret

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cryptic-pets-config
  namespace: cryptic-pets
data:
  PROJECT_NAME: "Cryptic Pets Backend"
  ENVIRONMENT: "production"
  API_V1_STR: "/api/v1"
  POSTGRES_SERVER: "postgres-service"
  POSTGRES_PORT: "5432"
  REDIS_PORT: "6379"
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cryptic-pets-secret
  namespace: cryptic-pets
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  POSTGRES_USER: <base64-encoded-user>
  POSTGRES_PASSWORD: <base64-encoded-password>
  POSTGRES_DB: <base64-encoded-db>
```

#### 3.3 PostgreSQL 部署

```yaml
# postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: cryptic-pets
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15.3
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: cryptic-pets-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: cryptic-pets-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: cryptic-pets-secret
              key: POSTGRES_DB
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: cryptic-pets
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

#### 3.4 应用部署

```yaml
# app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cryptic-pets-app
  namespace: cryptic-pets
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cryptic-pets-app
  template:
    metadata:
      labels:
        app: cryptic-pets-app
    spec:
      containers:
      - name: app
        image: cryptic-pets-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: cryptic-pets-secret
              key: SECRET_KEY
        envFrom:
        - configMapRef:
            name: cryptic-pets-config
        - secretRef:
            name: cryptic-pets-secret
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: cryptic-pets-service
  namespace: cryptic-pets
spec:
  selector:
    app: cryptic-pets-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 环境配置

### 1. 开发环境
```env
ENVIRONMENT=local
DEBUG=true
LOG_LEVEL=DEBUG
```

### 2. 测试环境
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
SENTRY_DSN=https://your-staging-sentry@sentry.io/project
```

### 3. 生产环境
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
SENTRY_DSN=https://your-production-sentry@sentry.io/project
```

## 监控和日志

### 1. 应用日志

查看应用日志：
```bash
# Docker 部署
docker-compose logs -f app

# Systemd 部署
sudo journalctl -u cryptic-pets -f

# Kubernetes 部署
kubectl logs -f deployment/cryptic-pets-app -n cryptic-pets
```

### 2. 性能监控

配置 Sentry 进行错误监控：
```python
# 在 main.py 中已配置
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)
```

### 3. 健康检查

添加健康检查端点：
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

## 备份和恢复

### 1. 数据库备份

```bash
# 创建备份
docker-compose exec postgres pg_dump -U cryptic_user cryptic_pets > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
docker-compose exec -T postgres psql -U cryptic_user cryptic_pets < backup_20240101_120000.sql
```

### 2. 定期备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/cryptic_pets_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker-compose exec -T postgres pg_dump -U cryptic_user cryptic_pets > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 清理7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

添加到 crontab：
```bash
# 每天凌晨2点执行备份
0 2 * * * /opt/scripts/backup.sh
```

## 安全配置

### 1. 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. SSL 证书

使用 Let's Encrypt：
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 数据库安全

PostgreSQL 安全配置：
```bash
# 编辑 pg_hba.conf
sudo vim /etc/postgresql/15/main/pg_hba.conf

# 修改认证方式为 md5
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
```

## 故障排除

### 1. 常见问题

**应用无法启动**
```bash
# 检查日志
docker-compose logs app

# 检查端口占用
netstat -tlnp | grep 8000

# 检查环境变量
docker-compose exec app env | grep POSTGRES
```

**数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U cryptic_user

# 检查连接配置
docker-compose exec app python -c "from infrastructure.config import settings; print(settings.SQLALCHEMY_DATABASE_URI)"
```

**性能问题**
```bash
# 检查资源使用
docker stats

# 检查数据库连接数
docker-compose exec postgres psql -U cryptic_user -d cryptic_pets -c "SELECT count(*) FROM pg_stat_activity;"
```

### 2. 维护命令

```bash
# 更新应用
git pull
docker-compose build
docker-compose up -d

# 清理 Docker 资源
docker system prune -a

# 重启服务
docker-compose restart app
sudo systemctl restart cryptic-pets
```

## 扩展部署

### 1. 负载均衡

使用 Nginx 配置多实例负载均衡：
```nginx
upstream cryptic_pets {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://cryptic_pets;
    }
}
```

### 2. 数据库主从复制

配置 PostgreSQL 主从复制以提高读性能和数据安全性。

### 3. Redis 集群

配置 Redis 集群以提高缓存性能和可用性。

## 联系支持

如在部署过程中遇到问题，请：
1. 查看相关日志文件
2. 检查配置文件设置
3. 提交 GitHub Issue
4. 联系技术支持团队
