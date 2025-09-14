"""
规约模式基础设施
提供规约模式的基础类和组合器
"""

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')


class Specification[T](ABC):
    """规约基类，定义规约接口"""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """检查候选对象是否满足规约"""
        pass

    def and_(self, other: 'Specification[T]') -> 'Specification[T]':
        """与另一个规约组合，使用AND逻辑"""
        return AndSpecification(self, other)

    def or_(self, other: 'Specification[T]') -> 'Specification[T]':
        """与另一个规约组合，使用OR逻辑"""
        return OrSpecification(self, other)

    def not_(self) -> 'Specification[T]':
        """否定当前规约"""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """AND组合规约，两个规约都必须满足"""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    """OR组合规约，两个规约至少一个满足"""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    """NOT规约，否定另一个规约"""

    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)


class AlwaysTrueSpecification(Specification[T]):
    """始终为真的规约，用作默认规约"""

    def is_satisfied_by(self, candidate: T) -> bool:
        return True


class AlwaysFalseSpecification(Specification[T]):
    """始终为假的规约"""

    def is_satisfied_by(self, candidate: T) -> bool:
        return False


class CompositeSpecification(Specification[T]):
    """复合规约，可以组合多个规约"""

    def __init__(self, specifications: list[Specification[T]]):
        self.specifications = specifications or []

    def add(self, specification: Specification[T]) -> 'CompositeSpecification[T]':
        """添加规约到复合规约中"""
        self.specifications.append(specification)
        return self

    def is_satisfied_by(self, candidate: T) -> bool:
        """默认实现为AND逻辑，子类可以重写"""
        return all(spec.is_satisfied_by(candidate) for spec in self.specifications)


class AnySpecification(CompositeSpecification[T]):
    """任意一个规约满足即可"""

    def is_satisfied_by(self, candidate: T) -> bool:
        """使用OR逻辑"""
        if not self.specifications:
            return True
        return any(spec.is_satisfied_by(candidate) for spec in self.specifications)


class AllSpecification(CompositeSpecification[T]):
    """所有规约都必须满足"""

    def is_satisfied_by(self, candidate: T) -> bool:
        """使用AND逻辑"""
        return all(spec.is_satisfied_by(candidate) for spec in self.specifications)


class ExpressionSpecification(Specification[T]):
    """基于表达式的规约，使用lambda表达式"""

    def __init__(self, expression):
        self.expression = expression

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.expression(candidate)
