from typing import TypeVar

from pydantic import BaseModel

from domain.pet_records.value_objects import PetEventTypeEnum

T = TypeVar("T", bound="PetRecordData")


class PetRecordData(BaseModel):
    """
    宠物记录数据基类（Value Object）
    所有宠物记录类型的数据都应继承此类
    """

    notes: str | None = None  # 公共备注字段，可存放额外信息


class FeedingRecordData(PetRecordData):
    """
    喂食记录数据
    """

    food_name: str  # 食物名称，如蟋蟀、红虫
    food_amount: float  # 喂食数量
    food_unit: str | None = "g"  # 喂食单位，默认克
    feeding_method: str | None = None  # 喂食方式，如手喂、碟喂
    description: str | None = None  # 详细备注或说明


class WeighingRecordData(PetRecordData):
    """
    称重记录数据
    """

    weight: float  # 体重数值
    weight_unit: str | None = "g"  # 体重单位，默认克
    scale_type: str | None = None  # 称重工具类型或型号
    condition: str | None = None  # 称重时宠物状态，如活跃、安静
    description: str | None = None  # 备注信息


class SheddingRecordData(PetRecordData):
    """
    蜕皮/换毛记录数据
    """

    shedding_area: str | None = None  # 蜕皮部位，如背部、尾巴
    shedding_degree: str | None = None  # 蜕皮程度，如轻度、中度、重度
    shedding_type: str | None = None  # 蜕皮类型，如整体、局部
    description: str | None = None  # 其他备注


class HealthRecordData(PetRecordData):
    """
    健康观察记录数据
    """

    symptom: str | None = None  # 症状描述
    severity: str | None = None  # 严重程度，如轻度、中度、重度
    treatment: str | None = None  # 是否进行治疗，及治疗方式
    vet_visit: bool | None = None  # 是否去过兽医
    description: str | None = None  # 其他备注


class BehaviorRecordData(PetRecordData):
    """
    行为观察记录数据
    """

    behavior_type: str | None = None  # 行为类型，如活动、进食、攻击
    duration_minutes: float | None = None  # 持续时间
    intensity: str | None = None  # 行为强度，如轻、中、强
    description: str | None = None  # 其他备注


class EnvironmentalRecordData(PetRecordData):
    """
    环境相关记录数据
    """

    temperature: float | None = None  # 温度
    humidity: float | None = None  # 湿度
    light_condition: str | None = None  # 光照情况
    description: str | None = None  # 其他备注


class OtherRecordData(PetRecordData):
    """
    其他类型记录数据
    """

    description: str | None = None  # 自定义记录描述


class PetRecordDataFactory:
    """宠物记录数据工厂类，用于根据事件类型创建对应的数据类"""

    # 事件类型到数据类的映射
    _TYPE_MAPPING: dict[PetEventTypeEnum, type[PetRecordData]] = {
        PetEventTypeEnum.FEEDING: FeedingRecordData,
        PetEventTypeEnum.WEIGHING: WeighingRecordData,
        PetEventTypeEnum.SHEDDING: SheddingRecordData,
        PetEventTypeEnum.HEALTH_CHECK: HealthRecordData,
        PetEventTypeEnum.BEHAVIOR: BehaviorRecordData,
        PetEventTypeEnum.ENVIRONMENT: EnvironmentalRecordData,
        PetEventTypeEnum.OTHER: OtherRecordData,
    }

    @classmethod
    def get_data_class(cls, event_type: PetEventTypeEnum) -> type[PetRecordData]:
        """根据事件类型获取对应的数据类

        Args:
            event_type: 宠物事件类型枚举

        Returns:
            对应的数据类

        Raises:
            ValueError: 当事件类型不支持时
        """
        if event_type not in cls._TYPE_MAPPING:
            raise ValueError(f"Unsupported event type: {event_type}")

        return cls._TYPE_MAPPING[event_type]

    @classmethod
    def create_data(cls, event_type: PetEventTypeEnum, **kwargs) -> PetRecordData:
        """根据事件类型创建对应的数据实例

        Args:
            event_type: 宠物事件类型枚举
            **kwargs: 数据字段参数

        Returns:
            创建的数据实例
        """
        data_class = cls.get_data_class(event_type)
        return data_class(**kwargs)

    @classmethod
    def parse_data(cls, event_type: PetEventTypeEnum, data: dict) -> PetRecordData:
        """根据事件类型解析数据字典为对应的数据实例

        Args:
            event_type: 宠物事件类型枚举
            data: 数据字典

        Returns:
            解析后的数据实例
        """
        data_class = cls.get_data_class(event_type)
        return data_class.model_validate(data)
