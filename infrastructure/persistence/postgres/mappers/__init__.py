"""Mapper模块初始化"""

from .base import BaseMapper
from .breed_mapper import BreedMapper
from .gene_mapper import GeneMapper
from .morph_gene_mapping_mapper import MorphGeneMappingMapper
from .morphology_mapper import MorphologyMapper
from .pet_mapper import PetMapper
from .user_mapper import UserMapper

__all__ = [
    "BaseMapper",
    "BreedMapper",
    "GeneMapper",
    "MorphGeneMappingMapper",
    "MorphologyMapper",
    "PetMapper",
    "UserMapper",
]
