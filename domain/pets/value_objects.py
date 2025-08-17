from enum import Enum


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

class PetTypeEnum(str, Enum):
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"

class InheritanceTypeEnum(str, Enum):
    DOMINANT = "dominant"  # 显性遗传
    RECESSIVE = "recessive"  # 隐性遗传
    X_LINKED = "x_linked"  # X染色体连锁遗传
    Y_LINKED = "y_linked"  # Y染色体连锁遗传
    AUTOSOMAL_DOMINANT = "autosomal_dominant"  # 常染色体显性遗传
    AUTOSOMAL_RECESSIVE = "autosomal_recessive"  # 常染色体隐性遗传
    OTHER = "other"  # 其他遗传方式

class GeneCategoryEnum(str, Enum):
    COLOR = "color"  # 颜色
    PATTERN = "pattern"  # 斑纹
    TEXTURE = "texture"  # 质地
    OTHER = "other"  # 其他

class ZygosityEnum(str, Enum):
    HOMOZYGOUS = "homozygous"  # 同源染色体同源基因
    HETEROZYGOUS = "heterozygous"  # 同源染色体异源基因
    UNKNOWN = "unknown"  # 未知
