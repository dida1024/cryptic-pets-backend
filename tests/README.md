# 测试指南

本文档介绍如何运行和编写 Cryptic Pets Backend 的测试。

## 测试结构

```
tests/
├── conftest.py              # 全局 pytest fixtures
├── unit/                    # 单元测试
│   ├── domain/              # 领域层单元测试
│   │   ├── test_user_entity.py
│   │   ├── test_pet_entity.py
│   │   └── test_pet_domain_service.py
│   └── application/         # 应用层单元测试
│       ├── test_user_handlers.py
│       └── test_pet_handlers.py
├── integration/             # 集成测试
│   ├── conftest.py          # 集成测试 fixtures
│   └── test_user_repository.py
└── e2e/                     # 端到端测试
    ├── conftest.py          # E2E 测试 fixtures
    ├── test_user_api.py
    └── test_pet_api.py
```

## 运行测试

### 安装测试依赖

```bash
# 使用 uv 安装开发依赖
uv sync --dev
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 带详细输出
pytest -v

# 带覆盖率报告
pytest --cov=domain --cov=application --cov=infrastructure --cov=interfaces --cov-report=html
```

### 运行特定测试

```bash
# 只运行单元测试
pytest tests/unit/

# 只运行领域层测试
pytest tests/unit/domain/

# 只运行特定测试文件
pytest tests/unit/domain/test_user_entity.py

# 只运行特定测试类
pytest tests/unit/domain/test_user_entity.py::TestUserEntity

# 只运行特定测试方法
pytest tests/unit/domain/test_user_entity.py::TestUserEntity::test_create_user_with_required_fields

# 运行匹配关键字的测试
pytest -k "user"
pytest -k "create and user"
```

### 运行集成测试

```bash
pytest tests/integration/ -v
```

### 运行端到端测试

```bash
pytest tests/e2e/ -v
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 生成终端覆盖率报告
pytest --cov=domain --cov=application --cov=infrastructure --cov=interfaces

# 生成 HTML 覆盖率报告
pytest --cov=domain --cov=application --cov=infrastructure --cov=interfaces --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 覆盖率目标

- **总体覆盖率**: ≥ 60%
- **领域层覆盖率**: ≥ 80%（核心业务逻辑）
- **应用层覆盖率**: ≥ 70%

## 编写测试

### 单元测试模板

```python
"""Unit tests for [Module Name]."""

import pytest
from domain.xxx.entities import Xxx


class TestXxxEntity:
    """Test cases for Xxx entity."""

    def test_create_with_required_fields(self):
        """Test creating entity with required fields."""
        entity = Xxx(name="test")
        assert entity.name == "test"

    def test_business_method(self):
        """Test a business method."""
        entity = Xxx(id="123", name="test")
        entity.do_something()
        assert entity.some_state == expected_value


class TestXxxDomainEvents:
    """Test cases for domain events."""

    def test_action_emits_event(self):
        """Test that action emits expected domain event."""
        entity = Xxx(id="123", name="test")
        entity.do_something()
        
        events = entity.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], XxxEvent)
```

### 集成测试模板

```python
"""Integration tests for [Repository Name]."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestXxxRepositoryIntegration:
    """Integration tests for XxxRepository."""

    @pytest.fixture
    def repository(self, db_session: AsyncSession) -> XxxRepository:
        """Create repository instance."""
        return PostgreSQLXxxRepositoryImpl(db_session, mapper, event_publisher)

    @pytest.mark.anyio
    async def test_create_and_retrieve(self, repository):
        """Test creating and retrieving an entity."""
        entity = Xxx(id="123", name="test")
        
        await repository.create(entity)
        result = await repository.get_by_id("123")
        
        assert result is not None
        assert result.name == "test"
```

### 端到端测试模板

```python
"""End-to-end tests for [API Name]."""

import pytest
from httpx import AsyncClient


class TestXxxAPI:
    """E2E tests for Xxx API."""

    @pytest.mark.anyio
    async def test_create_xxx(self, async_client: AsyncClient, api_v1_prefix: str):
        """Test creating Xxx via API."""
        response = await async_client.post(
            f"{api_v1_prefix}/xxx",
            json={"name": "test"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
```

## Fixtures

### 全局 Fixtures (tests/conftest.py)

- `sample_user` - 示例用户实体
- `sample_pet` - 示例宠物实体
- `mock_user_repository` - Mock 用户仓储
- `mock_pet_repository` - Mock 宠物仓储
- `mock_event_bus` - Mock 事件总线

### 集成测试 Fixtures (tests/integration/conftest.py)

- `async_engine` - 异步数据库引擎
- `db_session` - 数据库会话
- `event_publisher` - 事件发布器
- `*_mapper` - 各种映射器

### E2E 测试 Fixtures (tests/e2e/conftest.py)

- `async_client` - 异步 HTTP 客户端
- `api_v1_prefix` - API v1 前缀
- `user_payload` - 用户请求载荷
- `pet_payload` - 宠物请求载荷

## 最佳实践

1. **测试命名**: 使用描述性名称，如 `test_create_user_with_duplicate_email_raises_error`

2. **测试隔离**: 每个测试应该独立，不依赖其他测试的状态

3. **Mock 使用**: 单元测试使用 mock，集成测试使用真实依赖

4. **异步测试**: 使用 `@pytest.mark.anyio` 装饰器标记异步测试

5. **Fixtures**: 优先使用 fixtures 而非在测试中重复创建对象

## CI/CD 集成

在 CI 中运行测试：

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=domain --cov=application --cov=infrastructure --cov=interfaces \
           --cov-report=xml --cov-fail-under=60
```

