from enum import Enum


class PetEventTypeEnum(str, Enum):
    """
    宠物记录类型枚举
    用于区分不同类型的宠物记录
    """
    FEEDING = "FEEDING"             # 喂食记录
    WEIGHING = "WEIGHING"           # 称重记录
    SHEDDING = "SHEDDING"           # 蜕皮/换毛记录
    HEALTH_CHECK = "HEALTH_CHECK"   # 健康观察记录
    BEHAVIOR = "BEHAVIOR"           # 行为观察记录
    ENVIRONMENT = "ENVIRONMENT"     # 环境相关记录
    OTHER = "OTHER"                 # 其他记录
