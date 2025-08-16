# 开发指南

## 概述

本文档为 Cryptic Pets Backend 项目的开发人员提供详细的开发指南，包括开发环境搭建、代码规范、测试策略等内容。

## 开发环境搭建

### 1. 系统要求

- **Python**: 3.12+
- **Git**: 2.0+
- **Docker**: 20.10+ (可选)
- **IDE**: VS Code (推荐) / PyCharm

### 2. 项目克隆

```bash
git clone <repository-url>
cd cryptic-pets-backend
```

### 3. Python 环境配置

#### 使用 uv (推荐)

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

#### 使用传统方式

```bash
# 创建虚拟环境
python3.12 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -e .
```

### 4. 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

基本开发环境配置：
```env
# 项目配置
PROJECT_NAME=Cryptic Pets Backend
ROOTPATH=/
ENVIRONMENT=local

# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=cryptic_user
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=cryptic_pets_dev

# Redis 配置
REDIS_PORT=6379

# 安全配置
SECRET_KEY=dev_secret_key_123
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS 配置
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
FRONTEND_HOST=http://localhost:5173

# 日志配置
LOG_LEVEL=DEBUG
```

### 5. 数据库启动

使用 Docker Compose 启动开发数据库：
```bash
docker-compose up -d postgres redis
```

或手动安装：
```bash
# PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser -s cryptic_user
sudo -u postgres createdb -O cryptic_user cryptic_pets_dev

# Redis
sudo apt install redis-server
```

### 6. 数据库初始化

```bash
python -c "from infrastructure.persistence.postgres.init_db import init_db; init_db()"
```

### 7. 启动应用

```bash
# 开发模式启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用 VS Code 调试器
# 按 F5 启动调试
```

访问 http://localhost:8000/docs 查看 API 文档。

## 开发工具配置

### 1. VS Code 配置

#### 必装扩展

- Python
- Pylance
- Ruff
- GitLens
- Thunder Client (API 测试)
- Docker

#### 配置文件

创建 `.vscode/settings.json`：
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### 调试配置

`.vscode/launch.json` 已配置，支持：
- FastAPI 应用调试
- 自动重载
- 断点调试

### 2. PyCharm 配置

#### 项目设置

1. 打开项目目录
2. 设置 Python 解释器为虚拟环境
3. 配置运行配置：
   - Script path: `uvicorn`
   - Parameters: `main:app --reload`

## 代码规范

### 1. 代码格式化

项目使用 **Ruff** 进行代码格式化和检查：

```bash
# 检查代码
ruff check .

# 自动修复
ruff check . --fix

# 格式化代码
ruff format .
```

### 2. 类型检查

使用 **MyPy** 进行类型检查：

```bash
mypy .
```

### 3. 代码规范要点

#### 命名规范
- **类名**: PascalCase (`UserEntity`, `PaymentService`)
- **函数/变量名**: snake_case (`get_user`, `user_id`)
- **常量**: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)
- **私有成员**: 前缀下划线 (`_private_method`)

#### 类型注解
```python
# 必须的类型注解
def get_user_by_id(user_id: str) -> User | None:
    pass

# 复杂类型
from typing import List, Dict, Optional, Union

users: list[User] = []
user_map: dict[str, User] = {}
optional_user: User | None = None
```

#### 文档字符串
```python
def create_user(username: str, email: str) -> User:
    """创建新用户。
    
    Args:
        username: 用户名，必须唯一
        email: 邮箱地址，必须唯一
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        UserExistsError: 用户名或邮箱已存在
        ValidationError: 输入参数无效
    """
    pass
```

#### 导入规范
```python
# 标准库
import json
import logging
from datetime import datetime

# 第三方库
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# 本地导入
from domain.users.entities import User
from infrastructure.config import settings
```

### 4. Git 提交规范

#### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 类型说明
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档变更
- `style`: 代码格式化
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建或辅助工具变更

#### 示例
```bash
git commit -m "feat(user): add user registration endpoint

- Add user registration API
- Implement email validation
- Add password hashing

Closes #123"
```

## 项目结构详解

### 1. 目录结构
```
cryptic-pets-backend/
├── application/           # 应用层
│   └── users/            
│       ├── commands.py    # 命令对象
│       └── handlers.py    # 命令处理器
├── domain/               # 领域层
│   ├── base_entity.py    # 基础实体
│   └── users/
│       ├── entities.py    # 实体
│       ├── exceptions.py  # 领域异常
│       ├── repository.py  # 仓储接口
│       └── value_objects.py # 值对象
├── infrastructure/       # 基础设施层
│   ├── config.py         # 配置
│   ├── logging/          # 日志
│   └── persistence/      # 持久化
├── interfaces/           # 接口层
│   └── http/             # HTTP接口
└── tests/                # 测试
```

### 2. 分层职责

#### 领域层 (Domain)
- **职责**: 核心业务逻辑
- **原则**: 不依赖其他层
- **包含**: 实体、值对象、领域服务、仓储接口

```python
# domain/users/entities.py
class User(BaseEntity):
    username: str
    email: str
    
    def change_password(self, new_password: str) -> None:
        """修改密码业务逻辑"""
        if len(new_password) < 8:
            raise WeakPasswordError()
        self.hashed_password = hash_password(new_password)
        self._update_timestamp()
```

#### 应用层 (Application)
- **职责**: 用例协调，事务管理
- **原则**: 调用领域对象，不包含业务逻辑

```python
# application/users/handlers.py
class CreateUserHandler:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def handle(self, command: CreateUserCommand) -> User:
        # 检查用户是否存在
        existing = await self.user_repo.get_by_email(command.email)
        if existing:
            raise UserExistsError()
        
        # 创建用户
        user = User(
            username=command.username,
            email=command.email,
            hashed_password=hash_password(command.password)
        )
        
        return await self.user_repo.save(user)
```

#### 基础设施层 (Infrastructure)
- **职责**: 技术实现细节
- **原则**: 实现领域层定义的接口

```python
# infrastructure/persistence/postgres/repositories/user.py
class PostgreSQLUserRepository(UserRepository):
    async def save(self, user: User) -> User:
        # 数据库保存逻辑
        pass
    
    async def get_by_id(self, user_id: str) -> User | None:
        # 数据库查询逻辑
        pass
```

#### 接口层 (Interfaces)
- **职责**: 外部交互
- **原则**: 转换外部请求到应用层

```python
# interfaces/http/v1/routers/user.py
@router.post("/users", response_model=ApiResponse[UserResponse])
async def create_user(
    request: CreateUserRequest,
    handler: CreateUserHandler = Depends()
):
    command = CreateUserCommand(
        username=request.username,
        email=request.email,
        password=request.password
    )
    
    user = await handler.handle(command)
    return ApiResponse.success_response(
        data=UserResponse.from_entity(user)
    )
```

## 测试策略

### 1. 测试层次

#### 单元测试
- **范围**: 单个函数/方法
- **目标**: 领域逻辑、工具函数
- **工具**: pytest

```python
# tests/domain/users/test_entities.py
def test_user_change_password():
    user = User(username="test", email="test@example.com")
    user.change_password("new_password_123")
    assert user.hashed_password != "new_password_123"  # 应该被加密

def test_user_change_password_weak():
    user = User(username="test", email="test@example.com")
    with pytest.raises(WeakPasswordError):
        user.change_password("123")
```

#### 集成测试
- **范围**: 多个组件交互
- **目标**: 数据库操作、外部服务
- **工具**: pytest + testcontainers

```python
# tests/integration/test_user_repository.py
@pytest.mark.asyncio
async def test_user_repository_save(db_session):
    repo = PostgreSQLUserRepository(db_session)
    user = User(username="test", email="test@example.com")
    
    saved_user = await repo.save(user)
    assert saved_user.id is not None
    
    found_user = await repo.get_by_id(saved_user.id)
    assert found_user.username == "test"
```

#### 端到端测试
- **范围**: 完整请求流程
- **目标**: API接口
- **工具**: pytest + httpx

```python
# tests/e2e/test_user_api.py
@pytest.mark.asyncio
async def test_create_user_api(client):
    response = await client.post("/api/v1/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "testuser"
```

### 2. 测试配置

#### pytest 配置

创建 `pytest.ini`：
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

#### 测试固件

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from infrastructure.persistence.postgres.init_db import init_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def db_session():
    # 创建测试数据库会话
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/domain/users/test_entities.py

# 运行特定测试
pytest tests/domain/users/test_entities.py::test_user_change_password

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 只运行单元测试
pytest -m "not integration and not e2e"

# 运行集成测试
pytest -m integration

# 并行运行测试
pytest -n auto
```

## 数据库开发

### 1. 模型定义

#### 领域实体
```python
# domain/users/entities.py
class User(BaseEntity):
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    full_name: str | None = None
    hashed_password: str
    user_type: UserTypeEnum = UserTypeEnum.USER
    is_active: bool = True
    
    def is_admin(self) -> bool:
        return self.user_type == UserTypeEnum.ADMIN
```

#### 数据库模型
```python
# infrastructure/persistence/postgres/models/user.py
class UserModel(BaseModel, table=True):
    __tablename__ = "users"
    
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    hashed_password: str
    user_type: UserTypeEnum = UserTypeEnum.USER
    is_active: bool = True
```

### 2. 仓储模式

#### 接口定义
```python
# domain/users/repository.py
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass
    
    @abstractmethod
    async def list_users(self, limit: int, offset: int) -> list[User]:
        pass
```

#### 实现
```python
# infrastructure/persistence/postgres/repositories/user.py
class PostgreSQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, user: User) -> User:
        if user.id:
            # 更新
            stmt = select(UserModel).where(UserModel.id == user.id)
            result = await self.session.execute(stmt)
            db_user = result.scalar_one()
            
            for field, value in user.model_dump(exclude_unset=True).items():
                setattr(db_user, field, value)
        else:
            # 创建
            db_user = UserModel(**user.model_dump(exclude={"id"}))
            self.session.add(db_user)
        
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return User.model_validate(db_user)
    
    async def get_by_id(self, user_id: str) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        return User.model_validate(db_user) if db_user else None
```

### 3. 数据迁移

虽然项目使用 SQLModel 自动创建表，但对于生产环境建议使用 Alembic：

```bash
# 安装 Alembic
pip install alembic

# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Add users table"

# 执行迁移
alembic upgrade head
```

## Pydantic 数据验证

Cryptic Pets Backend 项目大量使用 Pydantic 进行数据验证，确保数据的完整性和类型安全。本章节详细介绍 Pydantic 的使用方法和最佳实践。

### 1. Pydantic 基础

#### 1.1 基本模型定义

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseModel):
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    age: int = Field(..., ge=18, le=120, description="年龄")
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        # 允许使用ORM模式
        from_attributes = True
        # 验证赋值
        validate_assignment = True
        # 使用枚举值
        use_enum_values = True
```

#### 1.2 字段验证

```python
from pydantic import BaseModel, Field, validator, root_validator
import re

class CreateUserRequest(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        regex=r'^[a-zA-Z0-9_]+$',
        description="用户名，只能包含字母、数字和下划线"
    )
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')
    
    @validator('username')
    def username_must_not_be_reserved(cls, v):
        reserved = ['admin', 'root', 'system', 'api']
        if v.lower() in reserved:
            raise ValueError('用户名不能使用保留关键字')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码必须包含至少一个特殊字符')
        return v
    
    @root_validator
    def passwords_match(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        if password != confirm_password:
            raise ValueError('两次输入的密码不一致')
        return values
```

### 2. 高级验证功能

#### 2.1 自定义验证器

```python
from pydantic import BaseModel, validator, ValidationError
from typing import Any
import phonenumbers

class ContactInfo(BaseModel):
    phone: str
    country_code: str = "CN"
    
    @validator('phone')
    def validate_phone(cls, v, values):
        try:
            country_code = values.get('country_code', 'CN')
            parsed_number = phonenumbers.parse(v, country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('无效的手机号码')
            return phonenumbers.format_number(
                parsed_number, 
                phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError('手机号码格式错误')

class BankAccount(BaseModel):
    account_number: str
    bank_code: str
    
    @validator('account_number')
    def validate_account(cls, v):
        # Luhn算法验证银行卡号
        def luhn_check(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10 == 0
        
        if not luhn_check(v):
            raise ValueError('无效的银行卡号')
        return v
```

#### 2.2 条件验证

```python
from pydantic import BaseModel, validator, root_validator
from typing import Optional

class PaymentRequest(BaseModel):
    payment_method: str  # "card", "bank", "wallet"
    card_number: Optional[str] = None
    bank_account: Optional[str] = None
    wallet_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    
    @root_validator
    def validate_payment_details(cls, values):
        method = values.get('payment_method')
        
        if method == 'card':
            if not values.get('card_number'):
                raise ValueError('信用卡支付需要提供卡号')
        elif method == 'bank':
            if not values.get('bank_account'):
                raise ValueError('银行转账需要提供银行账户')
        elif method == 'wallet':
            if not values.get('wallet_id'):
                raise ValueError('钱包支付需要提供钱包ID')
        else:
            raise ValueError('不支持的支付方式')
        
        return values
    
    @validator('amount')
    def validate_amount(cls, v, values):
        method = values.get('payment_method')
        
        # 不同支付方式的限额
        limits = {
            'card': 50000,
            'bank': 1000000,
            'wallet': 10000
        }
        
        if method in limits and v > limits[method]:
            raise ValueError(f'{method}支付单笔限额为{limits[method]}元')
        
        return v
```

### 3. 模型继承和组合

#### 3.1 基础模型

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BaseEntity(BaseModel):
    """基础实体模型"""
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)
    
    class Config:
        from_attributes = True
        validate_assignment = True

class TimestampMixin(BaseModel):
    """时间戳混入"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class SoftDeleteMixin(BaseModel):
    """软删除混入"""
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
```

#### 3.2 模型继承

```python
class User(BaseEntity):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)

class AdminUser(User):
    """管理员用户"""
    permissions: List[str] = Field(default_factory=list)
    access_level: int = Field(default=1, ge=1, le=10)
    
    @validator('permissions')
    def validate_permissions(cls, v):
        valid_permissions = [
            'user_management', 'content_management', 
            'system_settings', 'analytics'
        ]
        for perm in v:
            if perm not in valid_permissions:
                raise ValueError(f'无效的权限: {perm}')
        return v

class PublicUser(User):
    """公开用户信息"""
    username: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        # 排除敏感字段
        fields = {
            'email': {'exclude': True},
            'is_active': {'exclude': True}
        }
```

#### 3.3 模型组合

```python
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str = Field(..., regex=r'^\d{5}(-\d{4})?$')
    country: str = Field(default="CN")

class UserProfile(BaseModel):
    user_id: str
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    address: Optional[Address] = None
    social_links: Dict[str, str] = Field(default_factory=dict)
    
    @validator('social_links')
    def validate_social_links(cls, v):
        allowed_platforms = ['twitter', 'linkedin', 'github', 'website']
        for platform in v.keys():
            if platform not in allowed_platforms:
                raise ValueError(f'不支持的社交平台: {platform}')
        return v
```

### 4. 数据序列化和反序列化

#### 4.1 JSON序列化

```python
from pydantic import BaseModel, Field
import json
from datetime import datetime
from decimal import Decimal

class Product(BaseModel):
    name: str
    price: Decimal = Field(..., decimal_places=2)
    created_at: datetime
    tags: List[str]
    
    class Config:
        # 自定义JSON编码器
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

# 序列化
product = Product(
    name="商品名称",
    price=Decimal("99.99"),
    created_at=datetime.now(),
    tags=["电子产品", "数码"]
)

json_str = product.json()
dict_data = product.dict()

# 反序列化
product_from_json = Product.parse_raw(json_str)
product_from_dict = Product.parse_obj(dict_data)
```

#### 4.2 别名和字段映射

```python
class UserRequest(BaseModel):
    user_name: str = Field(..., alias="userName")
    email_address: EmailStr = Field(..., alias="emailAddress")
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    
    class Config:
        allow_population_by_field_name = True  # 允许使用字段名和别名

# 支持两种格式
data1 = {"userName": "john", "emailAddress": "john@example.com"}
data2 = {"user_name": "john", "email_address": "john@example.com"}

user1 = UserRequest.parse_obj(data1)
user2 = UserRequest.parse_obj(data2)
```

### 5. 错误处理和自定义异常

#### 5.1 验证错误处理

```python
from pydantic import ValidationError, BaseModel
from fastapi import HTTPException

def handle_validation_error(error: ValidationError) -> dict:
    """处理Pydantic验证错误"""
    formatted_errors = []
    
    for err in error.errors():
        field = " -> ".join(str(loc) for loc in err["loc"])
        formatted_errors.append({
            "field": field,
            "message": err["msg"],
            "type": err["type"]
        })
    
    return {
        "error": "数据验证失败",
        "details": formatted_errors
    }

# 在FastAPI中使用
@app.post("/users")
async def create_user(user_data: dict):
    try:
        user = CreateUserRequest.parse_obj(user_data)
        # 处理用户创建逻辑
        return {"success": True}
    except ValidationError as e:
        error_response = handle_validation_error(e)
        raise HTTPException(status_code=422, detail=error_response)
```

#### 5.2 自定义验证异常

```python
class BusinessValidationError(Exception):
    """业务验证异常"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class UserValidator:
    @staticmethod
    async def validate_unique_username(username: str, user_repo):
        """验证用户名唯一性"""
        existing = await user_repo.get_by_username(username)
        if existing:
            raise BusinessValidationError("username", "用户名已存在")
    
    @staticmethod
    async def validate_unique_email(email: str, user_repo):
        """验证邮箱唯一性"""
        existing = await user_repo.get_by_email(email)
        if existing:
            raise BusinessValidationError("email", "邮箱已被注册")

# 在应用层使用
async def create_user(request: CreateUserRequest, user_repo):
    # Pydantic基础验证已完成
    # 进行业务层验证
    await UserValidator.validate_unique_username(request.username, user_repo)
    await UserValidator.validate_unique_email(request.email, user_repo)
    
    # 创建用户
    user = User(**request.dict())
    return await user_repo.save(user)
```

### 6. 性能优化

#### 6.1 懒加载和缓存

```python
from functools import lru_cache
from pydantic import BaseModel, validator

class ConfigSettings(BaseModel):
    database_url: str
    redis_url: str
    secret_key: str
    
    @validator('database_url')
    @lru_cache(maxsize=1)
    def validate_db_url(cls, v):
        # 复杂的URL验证逻辑
        # 使用缓存避免重复验证
        return validate_database_url(v)

# 避免重复实例化
@lru_cache(maxsize=1)
def get_settings():
    return ConfigSettings()
```

#### 6.2 批量验证

```python
class BatchUserRequest(BaseModel):
    users: List[CreateUserRequest] = Field(..., max_items=100)
    
    @validator('users')
    def validate_batch_uniqueness(cls, v):
        # 批量验证用户名唯一性
        usernames = [user.username for user in v]
        if len(usernames) != len(set(usernames)):
            raise ValueError('批量创建的用户名不能重复')
        
        emails = [user.email for user in v]
        if len(emails) != len(set(emails)):
            raise ValueError('批量创建的邮箱不能重复')
        
        return v

# 批量处理
async def create_users_batch(batch_request: BatchUserRequest):
    # 预先验证所有数据
    validated_users = []
    for user_request in batch_request.users:
        user = User(**user_request.dict())
        validated_users.append(user)
    
    # 批量保存
    return await user_repo.save_batch(validated_users)
```

### 7. 与FastAPI集成

#### 7.1 自动API文档生成

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field, Schema

class CreateUserRequest(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="用户名，3-50个字符",
        example="john_doe"
    )
    email: EmailStr = Field(
        ..., 
        description="邮箱地址",
        example="john@example.com"
    )
    full_name: Optional[str] = Field(
        None, 
        description="用户全名",
        example="John Doe"
    )

@app.post("/users", response_model=UserResponse)
async def create_user(
    user: CreateUserRequest = Body(
        ...,
        description="用户创建请求",
        example={
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe"
        }
    )
):
    """
    创建新用户
    
    - **username**: 用户名，必须唯一
    - **email**: 邮箱地址，必须有效
    - **full_name**: 用户全名，可选
    """
    pass
```

#### 7.2 请求体验证

```python
from fastapi import FastAPI, HTTPException, Depends
from typing import Union

app = FastAPI()

# 多种请求格式支持
class CreateUserByEmail(BaseModel):
    email: EmailStr
    password: str

class CreateUserByPhone(BaseModel):
    phone: str
    password: str
    country_code: str = "CN"

CreateUserRequest = Union[CreateUserByEmail, CreateUserByPhone]

@app.post("/users")
async def create_user(user: CreateUserRequest):
    if isinstance(user, CreateUserByEmail):
        # 邮箱注册逻辑
        pass
    elif isinstance(user, CreateUserByPhone):
        # 手机号注册逻辑
        pass
```

### 8. 测试最佳实践

#### 8.1 模型测试

```python
import pytest
from pydantic import ValidationError

class TestUserModel:
    def test_valid_user_creation(self):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!"
        }
        user = CreateUserRequest(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_invalid_username(self):
        with pytest.raises(ValidationError) as exc_info:
            CreateUserRequest(
                username="ab",  # 太短
                email="test@example.com",
                password="Password123!"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("username",) for error in errors)
    
    def test_password_strength(self):
        weak_passwords = [
            "123456",      # 太简单
            "password",    # 没有大写字母和数字
            "PASSWORD123", # 没有小写字母
            "Password123", # 没有特殊字符
        ]
        
        for password in weak_passwords:
            with pytest.raises(ValidationError):
                CreateUserRequest(
                    username="testuser",
                    email="test@example.com",
                    password=password
                )
```

#### 8.2 工厂模式测试

```python
from factory import Factory, Faker, SubFactory
import factory

class UserFactory(Factory):
    class Meta:
        model = User
    
    username = Faker('user_name')
    email = Faker('email')
    full_name = Faker('name')
    is_active = True

class CreateUserRequestFactory(Factory):
    class Meta:
        model = CreateUserRequest
    
    username = Faker('user_name')
    email = Faker('email')
    password = "Password123!"
    confirm_password = "Password123!"

# 在测试中使用
def test_user_creation():
    request = CreateUserRequestFactory()
    user = User(**request.dict())
    assert user.username is not None
    assert user.email is not None
```

### 9. 实际应用示例

#### 9.1 复杂业务模型

```python
class PetRegistration(BaseModel):
    """宠物注册模型"""
    name: str = Field(..., min_length=1, max_length=50)
    species: str = Field(..., description="物种")
    breed: Optional[str] = Field(None, description="品种")
    birth_date: Optional[date] = None
    gender: str = Field(..., regex=r'^(male|female|unknown)$')
    color: str
    weight: Optional[float] = Field(None, gt=0, description="体重(kg)")
    vaccinations: List[str] = Field(default_factory=list)
    owner_id: str
    
    @validator('birth_date')
    def birth_date_not_future(cls, v):
        if v and v > date.today():
            raise ValueError('出生日期不能是未来的日期')
        return v
    
    @validator('vaccinations')
    def validate_vaccinations(cls, v):
        valid_vaccines = [
            'rabies', 'dhpp', 'bordetella', 'lyme', 'flea_tick'
        ]
        for vaccine in v:
            if vaccine not in valid_vaccines:
                raise ValueError(f'无效的疫苗类型: {vaccine}')
        return v
    
    @root_validator
    def validate_species_breed(cls, values):
        species = values.get('species')
        breed = values.get('breed')
        
        # 特定物种的品种验证
        valid_breeds = {
            'dog': ['labrador', 'golden_retriever', 'bulldog', 'poodle'],
            'cat': ['persian', 'siamese', 'maine_coon', 'british_shorthair']
        }
        
        if species in valid_breeds and breed:
            if breed not in valid_breeds[species]:
                raise ValueError(f'{species}不支持品种: {breed}')
        
        return values

class VeterinaryRecord(BaseModel):
    """兽医记录模型"""
    pet_id: str
    vet_name: str
    visit_date: date
    diagnosis: str
    treatment: str
    medications: List[str] = Field(default_factory=list)
    follow_up_date: Optional[date] = None
    cost: Decimal = Field(..., ge=0, decimal_places=2)
    
    @validator('follow_up_date')
    def follow_up_after_visit(cls, v, values):
        visit_date = values.get('visit_date')
        if v and visit_date and v <= visit_date:
            raise ValueError('复诊日期必须在就诊日期之后')
        return v
```

#### 9.2 API模型继承体系

```python
# 基础响应模型
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "操作成功"
    timestamp: datetime = Field(default_factory=datetime.now)

class DataResponse(BaseResponse, Generic[T]):
    data: Optional[T] = None

class ListResponse(BaseResponse, Generic[T]):
    data: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10

class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: str
    error_details: Optional[Dict] = None

# 具体使用
class UserListResponse(ListResponse[UserResponse]):
    pass

class PetResponse(BaseModel):
    id: str
    name: str
    species: str
    owner: UserResponse

class PetDetailResponse(DataResponse[PetResponse]):
    pass
```

### 10. 实用工具和技巧

#### 10.1 动态模型生成

```python
from pydantic import create_model
from typing import Dict, Any

def create_dynamic_user_model(fields: Dict[str, Any]):
    """动态创建用户模型"""
    field_definitions = {}
    
    for field_name, field_config in fields.items():
        field_type = field_config.get('type', str)
        field_default = field_config.get('default', ...)
        field_description = field_config.get('description', '')
        
        field_definitions[field_name] = (
            field_type, 
            Field(field_default, description=field_description)
        )
    
    return create_model('DynamicUser', **field_definitions)

# 使用示例
user_fields = {
    'username': {'type': str, 'description': '用户名'},
    'age': {'type': int, 'default': 18, 'description': '年龄'},
    'is_vip': {'type': bool, 'default': False, 'description': 'VIP状态'}
}

DynamicUser = create_dynamic_user_model(user_fields)
user = DynamicUser(username="test", age=25)
```

#### 10.2 模型转换工具

```python
class ModelConverter:
    """模型转换工具类"""
    
    @staticmethod
    def entity_to_response(entity: User) -> UserResponse:
        """实体转响应模型"""
        return UserResponse(**entity.dict(exclude={'hashed_password'}))
    
    @staticmethod
    def request_to_entity(request: CreateUserRequest) -> User:
        """请求转实体模型"""
        return User(
            **request.dict(exclude={'password', 'confirm_password'}),
            hashed_password=hash_password(request.password)
        )
    
    @staticmethod
    def batch_convert(items: List[Any], converter_func) -> List[Any]:
        """批量转换"""
        return [converter_func(item) for item in items]

# 使用示例
users = await user_repo.get_all()
user_responses = ModelConverter.batch_convert(
    users, 
    ModelConverter.entity_to_response
)
```

## API 开发

### 1. 路由定义

```python
# interfaces/http/v1/routers/user.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=ApiResponse[UserResponse])
async def create_user(
    request: CreateUserRequest,
    handler: Annotated[CreateUserHandler, Depends(get_create_user_handler)]
):
    try:
        command = CreateUserCommand(
            username=request.username,
            email=request.email,
            password=request.password
        )
        user = await handler.handle(command)
        return ApiResponse.success_response(
            data=UserResponse.from_entity(user),
            message="用户创建成功"
        )
    except UserExistsError:
        raise HTTPException(status_code=400, detail="用户已存在")
```

### 2. 请求/响应模型

```python
# interfaces/http/v1/models/user.py
class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None
    user_type: UserTypeEnum
    is_active: bool
    created_at: datetime
    
    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(**user.model_dump())
```

### 3. 依赖注入

```python
# interfaces/http/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.persistence.postgres.database import get_session
from infrastructure.persistence.postgres.repositories.user import PostgreSQLUserRepository
from application.users.handlers import CreateUserHandler

async def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> PostgreSQLUserRepository:
    return PostgreSQLUserRepository(session)

async def get_create_user_handler(
    user_repo: PostgreSQLUserRepository = Depends(get_user_repository)
) -> CreateUserHandler:
    return CreateUserHandler(user_repo)
```

### 4. 错误处理

```python
# interfaces/http/exceptions_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse

from domain.users.exceptions import UserExistsError, UserNotFoundError

async def user_exception_handler(request: Request, exc: UserExistsError):
    return JSONResponse(
        status_code=200,
        content=ApiResponse.error_response(
            message="用户已存在",
            code=1001
        ).model_dump()
    )

# 在 main.py 中注册
app.add_exception_handler(UserExistsError, user_exception_handler)
```

## 日志和监控

### 1. 日志配置

项目使用 Loguru 进行日志管理：

```python
# infrastructure/logging/config.py
from loguru import logger

def setup_logging():
    logger.remove()  # 移除默认处理器
    
    if settings.ENVIRONMENT == "development":
        logger.add(
            sys.stderr,
            level=settings.LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True
        )
    else:
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            serialize=True  # JSON 格式
        )
```

### 2. 日志使用

```python
from loguru import logger

class UserService:
    async def create_user(self, command: CreateUserCommand) -> User:
        logger.info("Creating user", username=command.username)
        
        try:
            user = await self.user_repo.save(user)
            logger.info("User created successfully", user_id=user.id)
            return user
        except Exception as e:
            logger.error("Failed to create user", error=str(e), username=command.username)
            raise
```

### 3. 性能监控

使用装饰器记录执行时间：

```python
import time
from functools import wraps

def log_execution_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                "Function executed",
                function=func.__name__,
                execution_time=execution_time
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Function failed",
                function=func.__name__,
                execution_time=execution_time,
                error=str(e)
            )
            raise
    return wrapper

class UserHandler:
    @log_execution_time
    async def handle(self, command: CreateUserCommand) -> User:
        # 处理逻辑
        pass
```

## 调试技巧

### 1. VS Code 调试

#### 断点调试
- 在代码行左侧点击设置断点
- 按 F5 启动调试
- 使用调试控制台查看变量

#### 条件断点
```python
# 右键断点设置条件
user_id == "specific_id"
```

### 2. 日志调试

```python
from loguru import logger

# 详细日志
logger.debug("Processing user data", user_data=user.model_dump())

# 结构化日志
logger.info("Database query", 
    query="SELECT * FROM users", 
    params={"id": user_id},
    execution_time=0.123
)
```

### 3. 交互式调试

```python
# 在代码中插入断点
import pdb; pdb.set_trace()

# 或使用 ipdb (更好的界面)
import ipdb; ipdb.set_trace()
```

### 4. 数据库调试

```python
# 打印 SQL 查询
engine = create_engine(database_url, echo=True)

# 在 SQLModel 查询中检查生成的SQL
stmt = select(UserModel).where(UserModel.id == user_id)
print(stmt)  # 查看 SQL 语句
```

## 性能优化

### 1. 数据库优化

#### 索引优化
```python
class UserModel(BaseModel, table=True):
    __tablename__ = "users"
    
    username: str = Field(index=True, unique=True)  # 添加索引
    email: str = Field(index=True, unique=True)     # 添加索引
    created_at: datetime = Field(index=True)        # 查询优化
```

#### 查询优化
```python
# 避免 N+1 查询
stmt = select(UserModel).options(selectinload(UserModel.posts))

# 分页查询
stmt = select(UserModel).offset(offset).limit(limit)

# 只查询需要的字段
stmt = select(UserModel.id, UserModel.username)
```

### 2. 缓存策略

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            redis_client.setex(
                cache_key, 
                expire_time, 
                json.dumps(result, default=str)
            )
            return result
        return wrapper
    return decorator

class UserService:
    @cache_result(expire_time=600)
    async def get_user_by_id(self, user_id: str) -> User:
        return await self.user_repo.get_by_id(user_id)
```

### 3. 异步优化

```python
import asyncio

# 并发执行多个操作
async def get_user_with_related_data(user_id: str):
    user_task = get_user_by_id(user_id)
    posts_task = get_user_posts(user_id)
    followers_task = get_user_followers(user_id)
    
    user, posts, followers = await asyncio.gather(
        user_task, posts_task, followers_task
    )
    
    return {
        "user": user,
        "posts": posts,
        "followers": followers
    }
```

## 最佳实践

### 1. 错误处理

```python
# 定义特定的业务异常
class UserExistsError(Exception):
    pass

class WeakPasswordError(Exception):
    pass

# 在应用层统一处理
try:
    user = await user_service.create_user(command)
except UserExistsError:
    raise HTTPException(status_code=400, detail="用户已存在")
except WeakPasswordError:
    raise HTTPException(status_code=400, detail="密码强度不足")
```

### 2. 配置管理

```python
# 使用 Pydantic Settings
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. 安全实践

```python
# 密码哈希
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT 令牌
import jwt

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

### 4. 文档编写

```python
class UserAPI:
    @router.post("/users", response_model=ApiResponse[UserResponse])
    async def create_user(
        self,
        request: CreateUserRequest,
        handler: CreateUserHandler = Depends()
    ):
        """
        创建新用户
        
        - **username**: 用户名，必须唯一
        - **email**: 邮箱地址，必须唯一且格式正确
        - **password**: 密码，至少8位字符
        - **full_name**: 全名，可选
        
        返回创建的用户信息，不包含敏感数据如密码。
        """
        pass
```

## 常见问题

### 1. 导入错误

```python
# 错误：循环导入
# 解决：使用类型检查时导入
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.users.entities import User
```

### 2. 数据库连接

```python
# 错误：未正确关闭连接
# 解决：使用上下文管理器
async with get_session() as session:
    # 数据库操作
    pass
```

### 3. 异步编程

```python
# 错误：在同步函数中调用异步函数
# 解决：使用 asyncio.run() 或确保调用者也是异步的
import asyncio

def sync_function():
    result = asyncio.run(async_function())
    return result
```

## 提交前检查清单

- [ ] 代码格式化 (`ruff format .`)
- [ ] 代码检查 (`ruff check .`)
- [ ] 类型检查 (`mypy .`)
- [ ] 运行测试 (`pytest`)
- [ ] 更新文档
- [ ] 提交信息符合规范
- [ ] 代码审查

## 获取帮助

### 内部资源
- 项目文档：`docs/`
- 代码示例：`examples/`
- 测试用例：`tests/`

### 外部资源
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)

### 团队支持
- 技术问题：提交 GitHub Issue
- 代码审查：创建 Pull Request
- 即时沟通：团队聊天群
