# 异常映射系统使用指南

## 概述

异常映射系统通过枚举的方式统一管理异常类型与错误码的对应关系，避免了在装饰器中硬编码异常处理逻辑。

## 系统架构

```
业务代码 → 抛出领域异常 → 装饰器捕获 → 异常映射系统 → BizException → 全局异常处理器
```

## 核心组件

### 1. ErrorCode 枚举

定义所有可能的错误码和默认消息：

```python
class ErrorCode(Enum):
    # 用户相关错误
    USER_NOT_FOUND = (404, "User not found")
    USER_ALREADY_EXISTS = (400, "User already exists")
    DUPLICATE_RESOURCE = (409, "Resource already exists")
    
    # 通用错误
    INVALID_PARAMETER = (400, "Invalid parameter")
    INTERNAL_ERROR = (500, "Internal server error")
```

### 2. ExceptionMapping 映射类

管理异常类型到错误码的映射关系：

```python
EXCEPTION_MAP: Dict[Type[Exception], ErrorCode] = {
    UserNotFoundError: ErrorCode.USER_NOT_FOUND,
    DuplicateUsernameError: ErrorCode.DUPLICATE_RESOURCE,
    ValueError: ErrorCode.INVALID_PARAMETER,
    Exception: ErrorCode.INTERNAL_ERROR,
}
```

### 3. 装饰器自动映射

```python
@handle_exceptions
async def my_endpoint():
    # 业务逻辑，直接抛出领域异常
    raise UserNotFoundError("User not found")
    # 装饰器自动映射为 BizException(404, "User not found")
```

## 使用方法

### 1. 基础使用

在业务代码中直接抛出领域异常：

```python
# 在用户服务中
if not user:
    raise UserNotFoundError(f"User with id '{user_id}' not found")

if username_exists:
    raise DuplicateUsernameError(f"Username '{username}' already exists")
```

装饰器会自动将这些异常映射为对应的业务异常：

```python
@handle_exceptions
async def create_user(request):
    # 如果抛出 DuplicateUsernameError
    # 自动映射为 BizException(409, "Username 'john' already exists")
    user = await user_service.create_user(command)
    return ApiResponse.success(data=user)
```

### 2. 添加新的错误码

在 `ErrorCode` 枚举中添加新的错误码：

```python
class ErrorCode(Enum):
    # 现有错误码...
    
    # 新增错误码
    PAYMENT_FAILED = (402, "Payment failed")
    QUOTA_EXCEEDED = (429, "Quota exceeded")
    SERVICE_UNAVAILABLE = (503, "Service temporarily unavailable")
```

### 3. 注册新的异常类型

#### 方法一：直接在映射中添加

```python
EXCEPTION_MAP: Dict[Type[Exception], ErrorCode] = {
    # 现有映射...
    
    # 新增映射
    PaymentError: ErrorCode.PAYMENT_FAILED,
    QuotaExceededError: ErrorCode.QUOTA_EXCEEDED,
}
```

#### 方法二：运行时注册

```python
# 注册预定义错误码
ExceptionMapping.register_exception(PaymentError, ErrorCode.PAYMENT_FAILED)

# 注册自定义错误码
ExceptionMapping.register_custom_exception(
    CustomError, 
    code=450, 
    message="Custom business error"
)
```

### 4. 创建新的领域异常

```python
# 在 domain/payment/exceptions.py
class PaymentDomainError(Exception):
    """支付领域基础异常"""
    pass

class PaymentFailedError(PaymentDomainError):
    """支付失败异常"""
    pass

class InsufficientFundsError(PaymentDomainError):
    """余额不足异常"""
    pass
```

然后在异常映射中注册：

```python
from domain.payment.exceptions import PaymentFailedError, InsufficientFundsError

EXCEPTION_MAP: Dict[Type[Exception], ErrorCode] = {
    # 现有映射...
    
    # 支付领域异常
    PaymentFailedError: ErrorCode.PAYMENT_FAILED,
    InsufficientFundsError: ErrorCode.PAYMENT_FAILED,
}
```

## 异常优先级

映射系统按照以下优先级查找异常：

1. **精确匹配**：`type(exception) in EXCEPTION_MAP`
2. **继承匹配**：`isinstance(exception, mapped_type)`
3. **默认处理**：`Exception -> INTERNAL_ERROR`

示例：

```python
# 优先级示例
EXCEPTION_MAP = {
    UserDomainError: ErrorCode.BUSINESS_ERROR,      # 基类
    UserNotFoundError: ErrorCode.USER_NOT_FOUND,    # 子类，优先级更高
}

# UserNotFoundError 会匹配到 USER_NOT_FOUND (404)，而不是 BUSINESS_ERROR (400)
```

## 最佳实践

### 1. 异常分层设计

```python
# 基础领域异常
class UserDomainError(Exception):
    pass

# 具体业务异常
class UserNotFoundError(UserDomainError):
    pass

class DuplicateUsernameError(UserDomainError):
    pass
```

### 2. 有意义的异常消息

```python
# 好的做法：提供具体信息
raise UserNotFoundError(f"User with id '{user_id}' not found")
raise DuplicateUsernameError(f"Username '{username}' already exists")

# 不好的做法：模糊的消息
raise UserNotFoundError("User not found")
raise DuplicateUsernameError("Duplicate username")
```

### 3. 异常映射组织

```python
# 按领域分组映射
EXCEPTION_MAP = {
    # === 用户领域 ===
    UserNotFoundError: ErrorCode.USER_NOT_FOUND,
    DuplicateUsernameError: ErrorCode.DUPLICATE_RESOURCE,
    
    # === 支付领域 ===
    PaymentFailedError: ErrorCode.PAYMENT_FAILED,
    InsufficientFundsError: ErrorCode.PAYMENT_FAILED,
    
    # === 通用异常 ===
    ValueError: ErrorCode.INVALID_PARAMETER,
    PermissionError: ErrorCode.PERMISSION_DENIED,
}
```

### 4. 错误码设计

```python
class ErrorCode(Enum):
    # 使用有意义的名称和适当的HTTP状态码
    USER_NOT_FOUND = (404, "User not found")           # 明确的语义
    DUPLICATE_RESOURCE = (409, "Resource already exists")  # 通用的重复错误
    VALIDATION_ERROR = (422, "Validation failed")       # 数据验证错误
    
    # 避免过于具体的错误码
    # USER_NOT_FOUND_BY_ID = (404, "User not found by id")  # 过于具体
    # USER_NOT_FOUND_BY_EMAIL = (404, "User not found by email")  # 过于具体
```

## 调试技巧

### 1. 查看异常映射结果

```python
from interfaces.http.exception_mapping import map_exception

try:
    raise UserNotFoundError("Test error")
except Exception as e:
    code, message = map_exception(e)
    print(f"Exception {type(e).__name__} -> code: {code}, message: {message}")
```

### 2. 检查映射配置

```python
from interfaces.http.exception_mapping import ExceptionMapping

# 查看所有映射
for exc_type, error_code in ExceptionMapping.EXCEPTION_MAP.items():
    print(f"{exc_type.__name__} -> {error_code.name} ({error_code.code})")
```

### 3. 测试异常处理

```python
# 创建测试用例验证异常映射
async def test_exception_mapping():
    @handle_exceptions
    async def test_func():
        raise UserNotFoundError("Test user not found")
    
    try:
        await test_func()
    except BizException as e:
        assert e.code == 404
        assert "Test user not found" in e.message
```

## 总结

异常映射系统提供了：

✅ **集中化管理**：所有异常映射在一处定义
✅ **类型安全**：编译时检查异常类型
✅ **易于扩展**：添加新异常类型很简单
✅ **一致性**：统一的错误处理策略
✅ **可维护性**：修改映射关系不影响业务代码
✅ **调试友好**：清晰的异常传播路径

这种设计使得异常处理既灵活又统一，是现代Web API开发的最佳实践。
