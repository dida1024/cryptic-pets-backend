from enum import Enum


class I18nEnum(str, Enum):
    """I18n enum."""
    ZH_CN = "zh_CN"
    EN_US = "en_US"

class PictureEnum(str, Enum):
    """Picture type enum."""
    BREED_JUVENILE = "breed_juvenile"  # 幼年图
    BREED_ADULT = "breed_adult"  # 成体图
    BREED_SUBADULT = "breed_subadult"  # 亚成图
    BREED_OTHER = "breed_other"  # 其他图
    PET_JUVENILE = "pet_juvenile"  # 幼年宠物图
    PET_ADULT = "pet_adult"  # 成体宠物图
    PET_SUBADULT = "pet_subadult"  # 亚成宠物图
    PET_OTHER = "pet_other"  # 其他宠物图

class EntityTypeEnum(str, Enum):
    """Entity type enum."""
    BREED = "breed"
    GENE = "gene"
    MORPHOLOGY = "morphology"
    PET = "pet"
