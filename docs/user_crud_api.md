# 用户CRUD API接口文档

## 概述
本文档描述了用户管理的基本CRUD（创建、读取、更新、删除）API接口。

## API端点

### 1. 创建用户
- **URL**: `POST /api/v1/users`
- **描述**: 创建新用户账户
- **请求体**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "strongpassword123",
  "user_type": "user",
  "is_active": true
}
```
- **响应**: 
```json
{
  "success": true,
  "code": 201,
  "message": "User created successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "user_type": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_deleted": false
  }
}
```

### 2. 获取用户详情
- **URL**: `GET /api/v1/users/{user_id}`
- **描述**: 根据用户ID获取用户详情
- **响应**: 用户对象

### 3. 更新用户信息
- **URL**: `PUT /api/v1/users/{user_id}`
- **描述**: 更新用户信息
- **请求体**:
```json
{
  "username": "johndoe_updated",
  "email": "john.updated@example.com",
  "full_name": "John Doe Updated",
  "user_type": "user",
  "is_active": true
}
```

### 4. 更新用户密码
- **URL**: `PATCH /api/v1/users/{user_id}/password`
- **描述**: 更新用户密码
- **请求体**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newstrongpassword123"
}
```

### 5. 删除用户
- **URL**: `DELETE /api/v1/users/{user_id}`
- **描述**: 删除用户（软删除）
- **响应**:
```json
{
  "success": true,
  "code": 200,
  "message": "User deleted successfully",
  "data": {
    "deleted": true
  }
}
```

### 6. 获取用户列表
- **URL**: `GET /api/v1/users`
- **描述**: 获取用户列表，支持搜索和过滤
- **查询参数**:
  - `page`: 页码 (默认: 1)
  - `page_size`: 每页数量 (默认: 10, 最大: 100)
  - `search`: 搜索关键字（用户名或邮箱）
  - `user_type`: 用户类型过滤 (admin/user/guest)
  - `is_active`: 激活状态过滤 (true/false)
  - `include_deleted`: 是否包含已删除用户 (默认: false)

- **响应**:
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "user_type": "user",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_deleted": false
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

## 用户类型枚举
- `admin`: 管理员
- `user`: 普通用户
- `guest`: 访客

## 错误处理
所有接口都会返回标准的错误响应格式：
```json
{
  "success": false,
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

常见错误代码：
- 400: 请求参数错误
- 404: 用户不存在
- 500: 服务器内部错误

## 架构说明

### 项目结构
```
interfaces/http/v1/
├── routers/
│   └── user.py              # 用户路由
└── schemas/
    └── user_schemas.py      # 请求/响应模型

application/users/
├── commands.py              # 应用层命令
└── handlers.py              # 用户服务处理器

domain/users/
├── entities.py              # 用户实体
├── repository.py            # 仓储接口
├── exceptions.py            # 用户异常
└── value_objects.py         # 值对象

infrastructure/persistence/postgres/
└── repositories/
    └── user_repository.py   # PostgreSQL用户仓储实现
```

### 技术栈
- **Web框架**: FastAPI
- **数据库**: PostgreSQL (通过SQLModel)
- **密码加密**: bcrypt (通过passlib)
- **架构模式**: 清洁架构 (Clean Architecture)
  - Interface层: HTTP路由和schemas
  - Application层: 业务逻辑处理
  - Domain层: 领域实体和业务规则
  - Infrastructure层: 数据持久化

### 数据验证
- 使用Pydantic进行请求数据验证
- 用户名: 3-50字符
- 密码: 最少8字符
- 邮箱: 标准邮箱格式验证

### 安全特性
- 密码哈希存储 (bcrypt)
- 软删除机制
- 数据唯一性验证 (用户名、邮箱)
- 输入数据验证和清理
