"""Base value object class with enhanced immutability and validation."""

from abc import ABC
from typing import Any

from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel, ABC):
    """Base class for all value objects with enhanced immutability and validation."""

    model_config = ConfigDict(
        frozen=True,  # Value objects are immutable
        validate_assignment=True,  # Validate on assignment
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_default=True,  # Validate default values
    )

    def __eq__(self, other: Any) -> bool:
        """Value objects are equal if they have the same type and content."""
        if not isinstance(other, self.__class__):
            return False
        return self.model_dump() == other.model_dump()

    def __hash__(self) -> int:
        """Value objects are hashable based on their content."""
        return hash(tuple(sorted(self.model_dump().items())))

    def __repr__(self) -> str:
        """String representation of the value object."""
        class_name = self.__class__.__name__
        fields = ", ".join(f"{k}={v!r}" for k, v in self.model_dump().items())
        return f"{class_name}({fields})"

    def copy_with(self, **updates: Any) -> "ValueObject":
        """Create a copy of this value object with updated fields."""
        return self.model_copy(update=updates)

    @classmethod
    def create(cls, **data: Any) -> "ValueObject":
        """Factory method to create a value object with validation."""
        return cls.model_validate(data)

    def is_valid(self) -> bool:
        """Check if the value object is in a valid state."""
        try:
            self.model_validate(self.model_dump())
            return True
        except Exception:
            return False
