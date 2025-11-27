# DDD 架构改进任务规划

> **创建日期**: 2025-11-27  
> **最后更新**: 2025-11-27  
> **状态**: 任务一、二、三、四、六已完成

---

## 📊 项目当前状态

| 维度 | 评分 | 说明 |
|------|------|------|
| 领域建模 | ⭐⭐⭐⭐☆ | ✅ 实体拥有丰富业务方法，密码等领域服务抽象完善 |
| 分层架构 | ⭐⭐⭐⭐☆ | 四层架构清晰，依赖方向正确 |
| 聚合设计 | ⭐⭐⭐⭐☆ | ✅ 聚合根使用一致，User/Pet/Breed/Gene/Morphology 统一继承 |
| 事件驱动 | ⭐⭐⭐☆☆ | 有事件机制，但缺少 Outbox 模式 |
| 测试覆盖 | ⭐⭐⭐☆☆ | ✅ 已建立完整测试框架，103个单元测试通过 |
| 工程实践 | ⭐⭐⭐☆☆ | 有日志监控，缺少幂等性和追踪 |

---

## 🚨 P0 - 必须修复（阻碍业务演进）

### 1. 测试覆盖严重不足

**问题描述**: 整个项目只有 `tests/domain/test_domain_events.py` 一个测试文件，核心业务逻辑没有测试保护。

**影响**: 无法保障代码质量，重构风险极高，新功能开发可能引入隐蔽 bug。

#### 任务清单

- [x] **1.1 创建测试目录结构** ✅
  ```
  tests/
  ├── conftest.py              # 全局 fixtures
  ├── unit/
  │   ├── domain/
  │   │   ├── test_user_entity.py
  │   │   ├── test_pet_entity.py
  │   │   └── test_pet_domain_service.py
  │   └── application/
  │       ├── test_user_handlers.py
  │       └── test_pet_handlers.py
  ├── integration/
  │   ├── conftest.py
  │   └── test_user_repository.py
  └── e2e/
      ├── conftest.py
      ├── test_user_api.py
      └── test_pet_api.py
  ```

- [x] **1.2 编写 User 实体单元测试** ✅
  - ✅ 测试用户创建
  - ✅ 测试实体相等性
  - ✅ 测试软删除
  - ✅ 测试领域事件

- [x] **1.3 编写 Pet 实体单元测试** ✅
  - ✅ 测试宠物创建
  - ✅ 测试所有权转移 (`change_owner`)
  - ✅ 测试品系更新 (`update_morphology`)
  - ✅ 测试领域事件触发

- [x] **1.4 编写 PetDomainService 单元测试** ✅
  - ✅ 测试 `create_pet_with_validation`
  - ✅ 测试 `transfer_pet_ownership`
  - ✅ 测试 `update_pet_morphology`
  - ✅ 测试各种边界情况和异常

- [x] **1.5 编写 Repository 集成测试** ✅
  - ✅ 使用 SQLite 内存数据库
  - ✅ 测试 CRUD 操作
  - ✅ 测试软删除
  - ✅ 测试分页查询

- [x] **1.6 编写 API 端到端测试** ✅
  - ✅ 使用 httpx AsyncClient
  - ✅ 测试用户 API 端点
  - ✅ 测试宠物 API 端点
  - ✅ 测试错误响应格式

- [x] **1.7 配置测试覆盖率报告** ✅
  - ✅ 添加 pytest-cov 依赖
  - ✅ 配置 pyproject.toml 中的覆盖率设置
  - ✅ 设定最低覆盖率阈值（当前 30%，待逐步提升）

---

### 2. 领域模型贫血问题

**问题描述**: `User`、`Pet` 等核心实体几乎只是数据容器，业务逻辑散落在 `Handler` 中。

**影响**: 违反面向对象设计原则，业务逻辑难以复用和测试。

#### 任务清单

- [x] **2.1 丰富 User 实体业务方法** ✅
  
  已添加的方法：
  - [x] `verify_password(plain_password, hasher)` - 验证密码
  - [x] `change_password(new_password, hasher)` - 修改密码
  - [x] `deactivate()` - 禁用账户
  - [x] `activate()` - 激活账户
  - [x] `promote_to_admin(promoted_by)` - 提升为管理员
  - [x] `demote_to_user()` - 降级为普通用户
  - [x] `update_profile(full_name, email)` - 更新个人信息
  - [x] `update_username(new_username)` - 更新用户名
  - [x] `change_user_type(new_user_type)` - 修改用户类型
  - [x] `is_admin()` / `is_guest()` / `can_login()` - 查询方法

- [x] **2.2 丰富 Pet 实体业务方法** ✅
  
  已添加的方法：
  - [x] `add_gene_mapping(gene_mapping)` - 添加基因映射
  - [x] `remove_gene_mapping(gene_id)` - 移除基因映射
  - [x] `add_picture(picture)` - 添加照片
  - [x] `remove_picture(picture_id)` - 移除照片
  - [x] `set_birth_date(date)` - 设置出生日期（带验证）
  - [x] `get_pet_age()` - 获取宠物年龄值对象
  - [x] `calculate_age_in_years()` / `calculate_age_in_months()` - 计算年龄
  - [x] `is_adult()` / `is_puppy()` / `is_senior()` - 判断生命阶段
  - [x] `get_life_stage()` / `get_formatted_age()` - 获取格式化信息
  - [x] `has_gene(gene_id)` / `get_gene_mapping(gene_id)` - 基因查询

- [x] **2.3 引入 PasswordHasher 接口** ✅
  
  ```python
  # domain/users/services.py
  class PasswordHasher(Protocol):
      def hash(self, password: str) -> str: ...
      def verify(self, password: str, hashed: str) -> bool: ...

  # infrastructure/security/bcrypt_hasher.py
  class BcryptPasswordHasher(PasswordHasher):
      ...
  ```

- [x] **2.4 引入 PasswordPolicy 领域服务** ✅
  
  ```python
  # domain/users/services.py
  class PasswordPolicy:
      def validate(self, password: str) -> None:
          # 验证密码强度（长度、大小写、数字、特殊字符）
          ...
  ```

- [x] **2.5 重构 CreateUserHandler** ✅
  - ✅ 移除密码哈希逻辑
  - ✅ 注入 PasswordHasher
  - ✅ 注入 PasswordPolicy 进行密码强度验证

- [x] **2.6 重构 UpdatePasswordHandler** ✅
  - ✅ 使用实体的 `verify_password` 和 `change_password` 方法
  - ✅ 注入 PasswordHasher
  - ✅ 注入 PasswordPolicy 验证新密码强度

---

### 3. 聚合根使用不一致

**问题描述**: `Pet` 继承自 `BaseEntity` 而非 `AggregateRoot`，但它明显是聚合根。

**影响**: 聚合设计不一致，领域事件管理混乱。

#### 任务清单

- [x] **3.1 修改 Pet 继承 AggregateRoot** ✅
  ```python
  # domain/pets/entities.py
  class Pet(AggregateRoot):  # 已修改为 AggregateRoot
      ...
  ```

- [x] **3.2 修改 User 继承 AggregateRoot** ✅
  ```python
  # domain/users/entities.py
  class User(AggregateRoot):  # 已修改为 AggregateRoot
      ...
  ```

- [x] **3.3 修改 Breed 继承 AggregateRoot** ✅
  ```python
  # domain/pets/entities.py
  class Breed(AggregateRoot):  # 已修改为 AggregateRoot
      ...
  ```

- [x] **3.4 审查并修改 Gene、Morphology** ✅
  - ✅ Gene 修改为 AggregateRoot（独立管理）
  - ✅ Morphology 修改为 AggregateRoot（独立管理）
  - ✅ MorphGeneMapping 保持为 BaseEntity（属于 Pet/Morphology 聚合内）

- [x] **3.5 更新所有 Repository 实现** ✅
  - ✅ Repository 已正确处理聚合根的领域事件
  - ✅ 使用 `add_domain_event` 替代 `_add_domain_event`

---

## ⚠️ P1 - 中短期优化

### 4. dependencies.py 过于庞大

**问题描述**: 单个文件超过 350 行，包含所有依赖注入配置。

#### 任务清单

- [x] **4.1 创建依赖模块目录结构** ✅
  ```
  infrastructure/dependencies/
  ├── __init__.py      # 统一导出，向后兼容
  ├── database.py      # 数据库会话
  ├── security.py      # 密码哈希和策略
  ├── mappers.py       # 映射器
  ├── repositories.py  # 仓储
  ├── users.py         # 用户相关
  ├── pets.py          # 宠物相关
  ├── breeds.py        # 品种相关
  └── pet_records.py   # 宠物记录相关
  ```

- [x] **4.2 拆分数据库相关依赖** ✅
  - ✅ `get_db_session` 移至 `database.py`

- [x] **4.3 拆分 Mapper 依赖** ✅
  - ✅ `get_user_mapper`, `get_pet_mapper` 等移至 `mappers.py`

- [x] **4.4 拆分 Repository 依赖** ✅
  - ✅ 各类 Repository 获取函数移至 `repositories.py`

- [x] **4.5 拆分 Handler 依赖** ✅
  - ✅ `users.py` - 用户命令/查询处理器
  - ✅ `pets.py` - 宠物命令/查询处理器 + 领域服务
  - ✅ `breeds.py` - 品种命令/查询处理器
  - ✅ `pet_records.py` - 宠物记录命令/查询处理器

- [x] **4.6 更新 __init__.py 导出** ✅
  - ✅ 所有依赖统一从 `__init__.py` 导出
  - ✅ 现有代码无需修改导入路径

---

### 5. 领域事件可靠性问题

**问题描述**: 无 Outbox 模式，事件发布与数据持久化不在同一事务，可能丢失事件。

#### 任务清单

- [ ] **5.1 创建 Outbox 表模型**
  ```python
  # infrastructure/persistence/postgres/models/outbox.py
  class OutboxEntry(SQLModel, table=True):
      __tablename__ = "outbox"
      
      id: str = Field(primary_key=True)
      event_type: str
      payload: str  # JSON
      created_at: datetime
      processed_at: datetime | None = None
  ```

- [ ] **5.2 修改 Repository 保存事件到 Outbox**
  - 在同一事务中保存实体和事件
  - 事件暂不直接发布

- [ ] **5.3 创建 Outbox 处理器**
  - 后台任务读取未处理的事件
  - 发布到 EventBus
  - 标记为已处理

- [ ] **5.4 添加 Outbox 清理任务**
  - 定期清理已处理的旧事件

- [ ] **5.5 添加重试机制**
  - 处理失败的事件重试
  - 死信队列

---

### 6. 全局 EventBus 单例问题

**问题描述**: 全局单例难以测试，且无法在不同上下文使用不同配置。

#### 任务清单

- [x] **6.1 修改 EventBus 为可注入** ✅
  - ✅ 添加 `EventBusProtocol` 协议接口
  - ✅ EventBus 可独立实例化，支持注入
  - ✅ 添加 `get_handlers_count()` 和 `has_handlers()` 辅助方法
  - ✅ 保留全局实例用于向后兼容

- [x] **6.2 更新 EventPublisher** ✅
  - ✅ 构造函数接收可选的 EventBus 参数
  - ✅ 添加 `create_event_publisher()` 工厂函数
  - ✅ 添加 `reset_global_event_publisher()` 用于测试

- [x] **6.3 更新依赖注入配置** ✅
  - ✅ 创建 `infrastructure/dependencies/events.py`
  - ✅ 添加 `get_event_bus()` 和 `get_event_publisher()` 依赖
  - ✅ 添加 `create_test_event_bus()` 和 `create_test_event_publisher()` 测试辅助函数
  - ✅ 更新 `event_registry.py` 支持注入 EventBus

- [x] **6.4 更新测试** ✅
  - ✅ 每个测试类使用 `@pytest.fixture` 创建独立 EventBus
  - ✅ 添加 `TestEventBusIsolation` 验证隔离性
  - ✅ 120 个测试全部通过

---

### 7. 区分领域事件与集成事件

**问题描述**: 所有事件使用同一基类，无法区分内部事件和跨服务事件。

#### 任务清单

- [ ] **7.1 创建 IntegrationEvent 基类**
  ```python
  # domain/common/events.py
  class IntegrationEvent(BaseModel, ABC):
      correlation_id: str = Field(default_factory=lambda: str(uuid4()))
      causation_id: str | None = None
  ```

- [ ] **7.2 定义集成事件**
  - 确定哪些事件需要跨服务通信
  - 创建对应的集成事件类

- [ ] **7.3 实现集成事件发布器**
  - 可能需要消息队列支持

---

## 📝 P2 - 长期改善

### 8. Bounded Context 边界不清

#### 任务清单

- [ ] **8.1 分析业务领域**
  - 识别核心域、支撑域、通用域
  - 绘制上下文映射图

- [ ] **8.2 设计目标目录结构**
  ```
  src/
  ├── identity/           # 用户身份上下文
  ├── pet_profile/        # 宠物档案上下文
  ├── feeding_journal/    # 饲养记录上下文
  └── genetics/           # 基因繁殖上下文
  ```

- [ ] **8.3 制定迁移计划**
  - 渐进式重构
  - 保持向后兼容

- [ ] **8.4 实施迁移**
  - 逐个上下文迁移
  - 更新依赖和导入

---

### 9. Repository 查询方法过多

#### 任务清单

- [ ] **9.1 设计 Specification 模式**
  ```python
  class Specification(ABC, Generic[T]):
      @abstractmethod
      def to_expression(self) -> Any: ...
      
      def and_(self, other: "Specification[T]") -> "Specification[T]": ...
      def or_(self, other: "Specification[T]") -> "Specification[T]": ...
  ```

- [ ] **9.2 实现通用查询方法**
  ```python
  class BaseRepository(ABC, Generic[T]):
      @abstractmethod
      async def find(self, spec: Specification[T]) -> list[T]: ...
      
      @abstractmethod
      async def find_one(self, spec: Specification[T]) -> T | None: ...
  ```

- [ ] **9.3 创建领域 Specification**
  - `PetsByOwnerSpec`
  - `PetsByBreedSpec`
  - `PetsByMorphologySpec`
  - 等等

- [ ] **9.4 重构现有 Repository**
  - 使用 Specification 替代特定方法

---

### 10. 工程实践完善

#### 任务清单

- [ ] **10.1 添加幂等性支持**
  - Command 添加 `idempotency_key` 字段
  - 创建幂等键存储表
  - 在 Handler 中检查重复

- [ ] **10.2 添加请求追踪**
  - 创建 request_id 中间件
  - 注入到日志上下文
  - 传递到下游服务

- [ ] **10.3 添加健康检查端点**
  - `/health` - 存活检查
  - `/ready` - 就绪检查（包含数据库连接）

- [ ] **10.4 添加 API 版本管理策略**
  - 文档化版本策略
  - 添加废弃标记机制

---

## 📅 里程碑计划

### 里程碑 1: 测试基础建设 (2 周) ✅ 已完成

| 任务 | 负责人 | 状态 | 完成日期 |
|------|--------|------|----------|
| 1.1 创建测试目录结构 | AI | ✅ 已完成 | 2025-11-27 |
| 1.2 编写 User 实体单元测试 | AI | ✅ 已完成 | 2025-11-27 |
| 1.3 编写 Pet 实体单元测试 | AI | ✅ 已完成 | 2025-11-27 |
| 1.4 编写 PetDomainService 单元测试 | AI | ✅ 已完成 | 2025-11-27 |
| 1.5 编写 Repository 集成测试 | AI | ✅ 已完成 | 2025-11-27 |
| 1.6 编写 API 端到端测试 | AI | ✅ 已完成 | 2025-11-27 |
| 1.7 配置测试覆盖率报告 | AI | ✅ 已完成 | 2025-11-27 |

**测试运行结果**: 98 个单元测试全部通过，覆盖率 33%（核心模块覆盖率更高）

### 里程碑 2: 领域模型重构 (3 周) ✅ 已完成

| 任务 | 负责人 | 状态 | 完成日期 |
|------|--------|------|----------|
| 2.1 丰富 User 实体业务方法 | AI | ✅ 已完成 | 2025-11-27 |
| 2.2 丰富 Pet 实体业务方法 | AI | ✅ 已完成 | 2025-11-27 |
| 2.3 引入 PasswordHasher 接口 | AI | ✅ 已完成 | 2025-11-27 |
| 2.4 引入 PasswordPolicy 领域服务 | AI | ✅ 已完成 | 2025-11-27 |
| 2.5-2.6 重构 Handler 使用新接口 | AI | ✅ 已完成 | 2025-11-27 |
| 3.1-3.4 修复聚合根继承 | AI | ✅ 已完成 | 2025-11-27 |
| 3.5 更新 Repository 实现 | AI | ✅ 已完成 | 2025-11-27 |

**完成内容**:
- User 实体新增 10+ 业务方法（密码验证、账户管理、角色变更等）
- Pet 实体新增 15+ 业务方法（基因管理、年龄计算、生命阶段判断等）
- 引入 PasswordHasher 接口和 BcryptPasswordHasher 实现
- 引入 PasswordPolicy 密码强度验证服务
- User/Pet/Breed/Gene/Morphology 统一继承 AggregateRoot
- 所有 103 个单元测试通过

### 里程碑 3: 架构优化 (4 周)

| 任务 | 负责人 | 状态 | 完成日期 |
|------|--------|------|----------|
| 4.1-4.6 拆分 dependencies.py | AI | ✅ 已完成 | 2025-11-27 |
| 5.1-5.5 实现 Outbox 模式 | - | ⬜ 待开始 | - |
| 6.1-6.4 重构 EventBus | AI | ✅ 已完成 | 2025-11-27 |

### 里程碑 4: 长期演进 (持续)

| 任务 | 负责人 | 状态 | 截止日期 |
|------|--------|------|----------|
| 8.1-8.4 Bounded Context 重组 | - | ⬜ 待开始 | - |
| 9.1-9.4 Specification 模式 | - | ⬜ 待开始 | - |
| 10.1-10.4 工程实践完善 | - | ⬜ 待开始 | - |

---

## 📌 状态说明

- ⬜ 待开始
- 🔄 进行中
- ✅ 已完成
- ❌ 已取消
- ⏸️ 已暂停

---

## 📝 变更日志

| 日期 | 变更内容 | 作者 |
|------|----------|------|
| 2025-11-27 | 创建任务规划文档 | AI Assistant |
| 2025-11-27 | 完成任务一：测试基础建设（98个测试通过） | AI Assistant |
| 2025-11-27 | 完成任务二：领域模型贫血问题修复（103个测试通过） | AI Assistant |
| 2025-11-27 | 完成任务三：聚合根使用不一致修复 | AI Assistant |
| 2025-11-27 | 完成任务四：dependencies.py 拆分为模块化结构 | AI Assistant |
| 2025-11-27 | 完成任务六：EventBus 重构为可注入（120个测试通过） | AI Assistant |

---

## 🔗 相关文档

- [架构设计文档](./architecture.md)
- [产品需求文档](./product_document.md)
- [异常处理架构](./exception_architecture.md)
- [开发指南](./development.md)

