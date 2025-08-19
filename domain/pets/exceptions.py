"""宠物领域异常"""

from domain.common.exceptions import (
    BusinessRuleViolationError,
    DomainError,
    EntityNotFoundError,
    RepositoryError,
)


class PetDomainError(DomainError):
    """宠物领域基础异常"""
    pass


class PetNotFoundError(EntityNotFoundError):
    """宠物未找到异常"""

    def __init__(self, pet_id: str):
        super().__init__("Pet", pet_id)


class BreedNotFoundError(EntityNotFoundError):
    """品种未找到异常"""

    def __init__(self, breed_id: str):
        super().__init__("Breed", breed_id)


class GeneNotFoundError(EntityNotFoundError):
    """基因未找到异常"""

    def __init__(self, gene_id: str):
        super().__init__("Gene", gene_id)


class MorphologyNotFoundError(EntityNotFoundError):
    """形态学未找到异常"""

    def __init__(self, morphology_id: str):
        super().__init__("Morphology", morphology_id)


class PetRepositoryError(RepositoryError):
    """宠物Repository异常"""
    pass


class BreedRepositoryError(RepositoryError):
    """品种Repository异常"""
    pass


class GeneRepositoryError(RepositoryError):
    """基因Repository异常"""
    pass


class MorphologyRepositoryError(RepositoryError):
    """形态学Repository异常"""
    pass


class InvalidGeneCombinatioError(BusinessRuleViolationError):
    """无效基因组合异常"""

    def __init__(self, message: str):
        super().__init__(message, "INVALID_GENE_COMBINATION")


class DuplicateGeneMappingError(BusinessRuleViolationError):
    """重复基因映射异常"""

    def __init__(self, gene_id: str, target_type: str):
        message = f"Gene {gene_id} already mapped to {target_type}"
        super().__init__(message, "DUPLICATE_GENE_MAPPING")

