from enum import Enum

from domain.users.exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserDomainError,
    UserNotActiveError,
    UserNotFoundError,
    WeakPasswordError,
)


class ErrorCode(Enum):
    """错误码枚举"""
    # 用户相关错误
    USER_NOT_FOUND = (404, "User not found")
    USER_ALREADY_EXISTS = (400, "User already exists")
    INVALID_CREDENTIALS = (401, "Invalid credentials")
    USER_NOT_ACTIVE = (403, "User account is not active")

    # 通用错误
    INVALID_PARAMETER = (400, "Invalid parameter")
    BUSINESS_ERROR = (400, "Business rule violation")
    PERMISSION_DENIED = (403, "Permission denied")
    RESOURCE_NOT_FOUND = (404, "Resource not found")
    INTERNAL_ERROR = (500, "Internal server error")

    # 数据验证错误
    VALIDATION_ERROR = (422, "Validation failed")
    DUPLICATE_RESOURCE = (409, "Resource already exists")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class ExceptionMapping:
    """异常映射配置类"""

    # 异常类型到错误码的映射
    EXCEPTION_MAP: dict[type[Exception], ErrorCode] = {
        # 用户领域异常映射 - 具体异常优先级更高
        UserNotFoundError: ErrorCode.USER_NOT_FOUND,
        UserAlreadyExistsError: ErrorCode.USER_ALREADY_EXISTS,
        DuplicateUsernameError: ErrorCode.DUPLICATE_RESOURCE,
        DuplicateEmailError: ErrorCode.DUPLICATE_RESOURCE,
        InvalidCredentialsError: ErrorCode.INVALID_CREDENTIALS,
        UserNotActiveError: ErrorCode.USER_NOT_ACTIVE,
        WeakPasswordError: ErrorCode.VALIDATION_ERROR,
        UserDomainError: ErrorCode.BUSINESS_ERROR,  # 基类异常，优先级较低

        # 通用异常映射
        ValueError: ErrorCode.INVALID_PARAMETER,
        PermissionError: ErrorCode.PERMISSION_DENIED,
        FileNotFoundError: ErrorCode.RESOURCE_NOT_FOUND,

        # 默认异常映射
        Exception: ErrorCode.INTERNAL_ERROR,
    }

    @classmethod
    def get_error_code(cls, exception: Exception) -> ErrorCode:
        """
        根据异常类型获取对应的错误码

        Args:
            exception: 异常实例

        Returns:
            ErrorCode: 对应的错误码枚举
        """
        exception_type = type(exception)

        # 直接查找异常类型
        if exception_type in cls.EXCEPTION_MAP:
            return cls.EXCEPTION_MAP[exception_type]

        # 查找父类异常类型
        for exc_type, error_code in cls.EXCEPTION_MAP.items():
            if isinstance(exception, exc_type):
                return error_code

        # 如果没有找到，返回内部错误
        return ErrorCode.INTERNAL_ERROR

    @classmethod
    def get_error_info(cls, exception: Exception) -> tuple[int, str]:
        """
        获取异常对应的错误码和消息

        Args:
            exception: 异常实例

        Returns:
            Tuple[int, str]: (错误码, 错误消息)
        """
        error_code = cls.get_error_code(exception)

        # 优先使用异常自身的消息，如果为空则使用默认消息
        exception_message = str(exception).strip()
        message = exception_message if exception_message else error_code.message

        return error_code.code, message

    @classmethod
    def register_exception(cls, exception_type: type[Exception], error_code: ErrorCode):
        """
        注册新的异常映射

        Args:
            exception_type: 异常类型
            error_code: 对应的错误码
        """
        cls.EXCEPTION_MAP[exception_type] = error_code

    @classmethod
    def register_custom_exception(cls, exception_type: type[Exception], code: int, message: str):
        """
        注册自定义异常映射

        Args:
            exception_type: 异常类型
            code: 错误码
            message: 错误消息
        """
        # 动态创建错误码枚举值
        custom_error = ErrorCode.__new__(ErrorCode)
        custom_error.code = code
        custom_error.message = message

        cls.EXCEPTION_MAP[exception_type] = custom_error


# 便捷的异常映射函数
def map_exception(exception: Exception) -> tuple[int, str]:
    """
    将异常映射为错误码和消息的便捷函数

    Args:
        exception: 异常实例

    Returns:
        Tuple[int, str]: (错误码, 错误消息)
    """
    return ExceptionMapping.get_error_info(exception)
