"""
宠物领域特定规约
实现针对Pet实体的规约模式
"""

from datetime import datetime, timedelta

from domain.common.specifications import Specification
from domain.pets.entities import Pet
from domain.pets.value_objects import GenderEnum


class PetByOwnerSpecification(Specification[Pet]):
    """按主人筛选宠物的规约"""

    def __init__(self, owner_id: str):
        self.owner_id = owner_id

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否属于指定主人"""
        return pet.owner_id == self.owner_id


class PetByBreedSpecification(Specification[Pet]):
    """按品种筛选宠物的规约"""

    def __init__(self, breed_id: str):
        self.breed_id = breed_id

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否属于指定品种"""
        return pet.breed_id == self.breed_id


class PetByMorphologySpecification(Specification[Pet]):
    """按品系筛选宠物的规约"""

    def __init__(self, morphology_id: str):
        self.morphology_id = morphology_id

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否具有指定品系"""
        return pet.morphology_id == self.morphology_id


class PetByGenderSpecification(Specification[Pet]):
    """按性别筛选宠物的规约"""

    def __init__(self, gender: GenderEnum):
        self.gender = gender

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否为指定性别"""
        return pet.gender == self.gender


class PetByNameSpecification(Specification[Pet]):
    """按名称筛选宠物的规约"""

    def __init__(self, name: str, exact_match: bool = False):
        self.name = name.lower()
        self.exact_match = exact_match

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物名称是否匹配"""
        if not pet.name:
            return False

        if self.exact_match:
            return pet.name.lower() == self.name
        else:
            return self.name in pet.name.lower()


class AdultPetSpecification(Specification[Pet]):
    """筛选成年宠物的规约"""

    def __init__(self, min_age_days: int = 365):
        self.min_age_days = min_age_days

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否成年（默认为1年以上）"""
        if not pet.birth_date:
            return False

        age_in_days = (datetime.now() - pet.birth_date).days
        return age_in_days >= self.min_age_days


class YoungPetSpecification(Specification[Pet]):
    """筛选幼年宠物的规约"""

    def __init__(self, max_age_days: int = 365):
        self.max_age_days = max_age_days

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否幼年（默认为1年以下）"""
        if not pet.birth_date:
            return False

        age_in_days = (datetime.now() - pet.birth_date).days
        return age_in_days < self.max_age_days


class PetCreatedInDateRangeSpecification(Specification[Pet]):
    """按创建日期范围筛选宠物的规约"""

    def __init__(self, start_date: datetime = None, end_date: datetime = None):
        self.start_date = start_date
        self.end_date = end_date or datetime.now()

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否在指定日期范围内创建"""
        if not pet.created_at:
            return False

        if self.start_date and pet.created_at < self.start_date:
            return False

        if self.end_date and pet.created_at > self.end_date:
            return False

        return True


class ActivePetSpecification(Specification[Pet]):
    """筛选活跃（未删除）宠物的规约"""

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否活跃（未删除）"""
        return not pet.is_deleted


class RecentlyCreatedPetSpecification(Specification[Pet]):
    """筛选最近创建的宠物的规约"""

    def __init__(self, days: int = 30):
        self.days = days
        self.cutoff_date = datetime.now() - timedelta(days=days)

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否在最近指定天数内创建"""
        if not pet.created_at:
            return False

        return pet.created_at >= self.cutoff_date


class RecentlyUpdatedPetSpecification(Specification[Pet]):
    """筛选最近更新的宠物的规约"""

    def __init__(self, days: int = 30):
        self.days = days
        self.cutoff_date = datetime.now() - timedelta(days=days)

    def is_satisfied_by(self, pet: Pet) -> bool:
        """检查宠物是否在最近指定天数内更新"""
        if not pet.updated_at:
            return False

        return pet.updated_at >= self.cutoff_date
