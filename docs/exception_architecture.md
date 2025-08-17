# 异常处理架构说明

## 架构概览

我们的异常处理采用了三层架构：

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   API 接口层     │───▶│   装饰器中间层    │───▶│   全局异常处理器    │
│  (@handle_      │    │  (领域异常 →     │    │  (BizException →   │
│   exceptions)   │    │   BizException)  │    │   统一JSON响应)    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

## 异常处理流程

### 1. 接口层 - 使用装饰器

```python
@router.post("/users")
@handle_exceptions  # 装饰器自动处理异常
async def create_user(request, user_service):
    # 只需要写业务逻辑，无需try-catch
    user = await user_service.create_user(command)
    return ApiResponse.success(data=user_response)
```

### 2. 装饰器层 - 转换异常类型

```python
@handle_exceptions
async def wrapper(*args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except UserNotFoundError as e:
        raise BizException(code=404, message=str(e))  # 转换为业务异常
    except ValueError as e:
        raise BizException(code=400, message=str(e))
    # ... 其他异常映射
```

### 3. 全局处理器 - 统一响应格式

```python
async def biz_exception_handler(request: Request, exc: BizException):
    return JSONResponse(
        status_code=200,  # HTTP状态码始终200
        content=ApiResponse.error(
            message=exc.message,
            code=exc.code      # 业务错误码
        ).model_dump()
    )
```

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { "用户数据..." }
}
```

### 错误响应
```json
{
  "code": 404,        // 业务错误码
  "message": "User with id 'xxx' not found",
  "data": null
}
```

**重要**：所有响应的HTTP状态码都是200，通过 `code` 字段传递业务状态。

## 异常映射表

| 领域异常 | 业务错误码 | 说明 |
|---------|-----------|------|
| `UserNotFoundError` | 404 | 用户未找到 |
| `ValueError` | 400 | 参数错误/业务规则违反 |
| `UserDomainError` | 400 | 用户领域异常 |
| `BizException` | 原样传递 | 已经是业务异常，直接传递 |
| `Exception` | 500 | 未预期的系统错误 |

## 关键设计原则

### 1. **统一的HTTP状态码**
- 所有API响应都返回HTTP 200
- 通过业务错误码区分成功/失败状态
- 避免了HTTP状态码的复杂性

### 2. **分层异常处理**
- **接口层**：无需关心异常处理
- **装饰器层**：负责异常类型转换
- **全局处理器**：负责响应格式统一

### 3. **DRY原则**
- 异常处理逻辑集中在装饰器
- 避免在每个接口重复try-catch
- 全局处理器保证响应格式一致

### 4. **可扩展性**
- 添加新异常类型只需修改装饰器
- 修改响应格式只需修改全局处理器
- 业务逻辑与异常处理完全解耦

## 使用指南

### 1. 在接口上使用装饰器
```python
@router.post("/endpoint")
@handle_exceptions
async def my_endpoint():
    # 业务逻辑，直接抛出领域异常
    if not user:
        raise UserNotFoundError("用户不存在")
    return ApiResponse.success(data=result)
```

### 2. 在业务逻辑中抛出合适的异常
```python
# 用户服务中
if not user:
    raise UserNotFoundError(f"User with id '{user_id}' not found")

if password_invalid:
    raise ValueError("Password is incorrect")
```

### 3. 自定义业务异常（可选）
```python
# 直接抛出业务异常，跳过装饰器转换
raise BizException(code=422, message="自定义业务错误")
```

## 优势总结

✅ **简化接口代码**：接口只需关注业务逻辑
✅ **统一错误格式**：所有错误响应格式一致  
✅ **HTTP状态简化**：避免复杂的HTTP状态码管理
✅ **易于维护**：异常处理逻辑集中管理
✅ **类型安全**：明确的异常类型映射
✅ **可扩展**：容易添加新的异常类型

这种架构特别适合前后端分离的项目，前端只需要检查 `code` 字段就能判断操作是否成功。
