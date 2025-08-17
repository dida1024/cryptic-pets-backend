# 异常处理装饰器重构文档

## 重构目标
使用装饰器统一处理API异常，避免在每个接口中重复编写try-catch代码块。

## 装饰器设计

### 核心装饰器：`@handle_exceptions`

```python
@handle_exceptions
async def create_user(request, user_service) -> ApiResponse[UserResponse]:
    # 只需要写核心业务逻辑，异常自动处理
    command = CreateUserCommand(...)
    user = await user_service.create_user(command)
    return ApiResponse.success(data=user_response)
```

### 异常映射规则

装饰器会将领域异常转换为业务异常 `BizException`，然后由全局异常处理器统一处理：

| 异常类型 | 业务错误码 | 描述 |
|---------|-----------|------|
| `UserNotFoundError` | 404 | 用户未找到 |
| `ValueError` | 400 | 参数错误或业务规则违反 |
| `UserDomainError` | 400 | 用户领域异常 |
| `Exception` | 500 | 未预期的服务器内部错误 |

**注意**：所有响应的HTTP状态码都是200，错误信息通过业务错误码传递。

## 重构前后对比

### 重构前的代码（冗长）

```python
@router.post("/users")
async def create_user(request, user_service) -> ApiResponse[UserResponse]:
    """创建用户"""
    try:
        command = CreateUserCommand(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            user_type=request.user_type,
            is_active=request.is_active,
        )

        user = await user_service.create_user(command)
        user_response = UserResponse.model_validate(user.model_dump())

        return ApiResponse.success(
            data=user_response,
            message="User created successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### 重构后的代码（简洁）

```python
@router.post("/users")
@handle_exceptions
async def create_user(request, user_service) -> ApiResponse[UserResponse]:
    """创建用户"""
    command = CreateUserCommand(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        user_type=request.user_type,
        is_active=request.is_active,
    )

    user = await user_service.create_user(command)
    user_response = UserResponse.model_validate(user.model_dump())

    return ApiResponse.success(
        data=user_response,
        message="User created successfully"
    )
```

## 代码改进效果

### 1. **代码量减少**
- 每个接口减少约 15-20 行异常处理代码
- 5个接口总共减少约 80+ 行重复代码

### 2. **可维护性提升**
- 异常处理逻辑集中在装饰器中
- 修改异常处理策略只需要修改一处
- 添加新的异常类型映射非常简单

### 3. **代码可读性提升**
- 接口函数只关注核心业务逻辑
- 清晰的职责分离：业务逻辑 vs 异常处理
- 减少了认知负担

### 4. **一致性保证**
- 所有接口使用相同的异常处理策略
- 统一的错误响应格式
- 避免了手动处理时的疏漏

## 装饰器实现细节

### 完整装饰器代码

```python
def handle_exceptions(func: Callable) -> Callable:
    """
    异常处理装饰器

    自动捕获并转换异常为业务异常：
    - UserNotFoundError -> BizException(404, message)
    - ValueError -> BizException(400, message)
    - UserDomainError -> BizException(400, message)
    - Exception -> BizException(500, "Internal server error")
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except UserNotFoundError as e:
            raise BizException(code=404, message=str(e))
        except ValueError as e:
            raise BizException(code=400, message=str(e))
        except UserDomainError as e:
            raise BizException(code=400, message=str(e))
        except BizException:
            # 如果已经是业务异常，直接重新抛出
            raise
        except Exception as e:
            # 记录未预期的异常（可以添加日志）
            # logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise BizException(code=500, message="Internal server error")

    return wrapper
```

### 业务异常类

```python
class BizException(Exception):
    """基础业务异常"""
    def __init__(self, code: int = 400, message: str = "业务异常"):
        self.code = code
        self.message = message
```

### 全局异常处理器

```python
async def biz_exception_handler(request: Request, exc: BizException):
    return JSONResponse(
        status_code=200,  # 不抛 HTTP 错
        content=ApiResponse.error(
            message=exc.message,
            code=exc.code
        ).model_dump()
    )

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,  # 不抛 HTTP 错
        content=ApiResponse.error(
            message=str(exc),
            code=500,
            data=str(exc)
        ).model_dump()
    )
```

### 可选装饰器：`@handle_business_exceptions`

```python
@handle_business_exceptions  # 只处理业务异常，不处理通用异常
async def special_endpoint():
    # 让意外异常继续传播到全局异常处理器
    pass
```

## 使用指南

### 1. **标准用法**
```python
@router.post("/endpoint")
@handle_exceptions
async def my_endpoint():
    # 业务逻辑
    pass
```

### 2. **装饰器顺序**
- `@handle_exceptions` 应该放在路由装饰器之后
- 确保异常处理是最外层的包装

### 3. **异常传播**
- 业务逻辑中直接抛出相应的异常
- 装饰器会自动捕获并转换为HTTP响应

### 4. **日志集成**
装饰器中预留了日志记录位置，可以很容易地添加日志功能：

```python
except Exception as e:
    logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
    raise HTTPException(...)
```

## 扩展性

### 添加新的异常类型

```python
except CustomBusinessError as e:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(e)
    )
```

### 创建特定领域的装饰器

```python
def handle_payment_exceptions(func: Callable) -> Callable:
    # 专门处理支付相关异常
    pass
```

## 总结

通过引入异常处理装饰器，我们实现了：

✅ **DRY原则**: 消除了重复的异常处理代码
✅ **关注点分离**: 业务逻辑与异常处理分离
✅ **一致性**: 统一的异常处理策略
✅ **可维护性**: 集中式的异常处理逻辑
✅ **可扩展性**: 易于添加新的异常类型
✅ **可读性**: 接口代码更简洁易懂

这种重构方式是现代Web API开发的最佳实践，值得在其他项目中推广使用。
