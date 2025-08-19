"""领域层通用异常定义"""


class DomainError(Exception):
    """领域层基础异常"""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class EntityNotFoundError(DomainError):
    """实体未找到异常"""

    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(message, "ENTITY_NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id


class RepositoryError(DomainError):
    """Repository操作异常"""

    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "REPOSITORY_ERROR")
        self.operation = operation


class ConcurrencyError(DomainError):
    """并发冲突异常"""

    def __init__(self, entity_type: str, entity_id: str):
        message = f"Concurrency conflict for {entity_type} with id '{entity_id}'"
        super().__init__(message, "CONCURRENCY_CONFLICT")
        self.entity_type = entity_type
        self.entity_id = entity_id


class ValidationError(DomainError):
    """验证异常"""

    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class BusinessRuleViolationError(DomainError):
    """业务规则违反异常"""

    def __init__(self, message: str, rule: str = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
        self.rule = rule
