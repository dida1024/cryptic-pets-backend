import datetime
import uuid

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    model_config = {
        "arbitrary_types_allowed": True  # 允许使用任意类型，包括 datetime
    }

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    created_at: datetime = Field(
        default_factory=datetime.datetime.now,
        sa_type=DateTime(timezone=True),
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=datetime.datetime.now,
        sa_type=DateTime(timezone=True),
        nullable=False
    )

    is_deleted: bool = Field(default=False, nullable=False)
