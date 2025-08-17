import functools
from collections.abc import Callable
from typing import Any

from loguru import logger

from interfaces.http.exception_mapping import map_exception
from interfaces.http.exceptions_handler import BizException


def handle_exceptions(func: Callable) -> Callable:
    """
    异常处理装饰器

    使用异常映射系统自动转换异常为业务异常
    异常映射配置在 exception_mapping.py 中定义
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except BizException:
            # 如果已经是业务异常，直接重新抛出
            raise
        except Exception as e:
            # 使用异常映射系统获取错误码和消息
            code, message = map_exception(e)

            # 对于未预期的异常（500错误），记录详细日志
            if code == 500:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)

            raise BizException(code=code, message=message)

    return wrapper

