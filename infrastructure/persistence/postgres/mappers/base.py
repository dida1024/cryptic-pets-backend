from abc import ABC, abstractmethod
from typing import TypeVar

DomainEntity = TypeVar('DomainEntity')
DatabaseModel = TypeVar('DatabaseModel')


class BaseMapper[DomainEntity, DatabaseModel](ABC):
    """基础Mapper接口，定义实体与模型转换"""

    @abstractmethod
    def to_domain(self, model: DatabaseModel) -> DomainEntity:
        """数据库模型转换为领域实体"""
        pass

    @abstractmethod
    def to_model(self, entity: DomainEntity) -> DatabaseModel:
        """领域实体转换为数据库模型"""
        pass

    def to_domain_list(self, models: list[DatabaseModel]) -> list[DomainEntity]:
        """批量转换数据库模型为领域实体"""
        return [self.to_domain(model) for model in models]

    def to_model_list(self, entities: list[DomainEntity]) -> list[DatabaseModel]:
        """批量转换领域实体为数据库模型"""
        return [self.to_model(entity) for entity in entities]

    def to_domain_optional(self, model: DatabaseModel | None) -> DomainEntity | None:
        """可选的数据库模型转换为领域实体"""
        return self.to_domain(model) if model is not None else None

    def to_model_optional(self, entity: DomainEntity | None) -> DatabaseModel | None:
        """可选的领域实体转换为数据库模型"""
        return self.to_model(entity) if entity is not None else None
