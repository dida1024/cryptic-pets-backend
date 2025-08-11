import datetime
import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    model_config = {
        "arbitrary_types_allowed": True  # 允许使用任意类型，包括 datetime
    }

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    is_deleted: bool = Field(default=False, nullable=False)
