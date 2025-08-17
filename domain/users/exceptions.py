"""用户领域异常"""


class UserDomainError(Exception):
    """用户领域基础异常"""
    pass


class UserNotFoundError(UserDomainError):
    """用户未找到异常"""
    pass


class UserAlreadyExistsError(UserDomainError):
    """用户已存在异常"""
    pass


class InvalidCredentialsError(UserDomainError):
    """无效凭据异常"""
    pass


class UserNotActiveError(UserDomainError):
    """用户未激活异常"""
    pass


class DuplicateUsernameError(UserDomainError):
    """用户名重复异常"""
    pass


class DuplicateEmailError(UserDomainError):
    """邮箱重复异常"""
    pass


class WeakPasswordError(UserDomainError):
    """密码强度不足异常"""
    pass
