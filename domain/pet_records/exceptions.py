"""用户领域异常"""


class PetRecordDomainError(Exception):
    """记录领域基础异常"""
    pass


class PetRecordNotFoundError(PetRecordDomainError):
    """记录未找到异常"""
    pass


class PetRecordAlreadyExistsError(PetRecordDomainError):
    """记录已存在异常"""
    pass


class InvalidCredentialsError(PetRecordDomainError):
    """无效凭据异常"""
    pass


class DuplicateUsernameError(PetRecordDomainError):
    """记录类型重复异常"""
    pass


class DuplicateEmailError(PetRecordDomainError):
    """记录类型重复异常"""
    pass


class WeakPasswordError(PetRecordDomainError):
    """记录类型重复异常"""
    pass
