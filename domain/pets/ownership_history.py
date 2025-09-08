"""Ownership history value object for tracking pet ownership changes."""

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from domain.common.value_object_base import ValueObject


class OwnershipRecord(ValueObject):
    """Individual ownership record value object."""

    owner_id: str = Field(..., description="Owner's user ID")
    owner_name: str | None = Field(None, description="Owner's name at time of ownership")
    start_date: datetime = Field(..., description="Start date of ownership")
    end_date: datetime | None = Field(None, description="End date of ownership (None for current owner)")
    transfer_reason: str | None = Field(None, description="Reason for ownership transfer")
    transfer_type: str = Field(default="transfer", description="Type of transfer (transfer, adoption, purchase, etc.)")

    @field_validator('owner_id')
    @classmethod
    def validate_owner_id(cls, v: str) -> str:
        """Validate owner ID."""
        if not v or not v.strip():
            raise ValueError("Owner ID cannot be empty")
        return v.strip()

    @field_validator('owner_name')
    @classmethod
    def validate_owner_name(cls, v: str | None) -> str | None:
        """Validate owner name."""
        if v is not None and not v.strip():
            raise ValueError("Owner name cannot be empty")
        return v.strip() if v else None

    @field_validator('transfer_reason')
    @classmethod
    def validate_transfer_reason(cls, v: str | None) -> str | None:
        """Validate transfer reason."""
        if v is not None and not v.strip():
            raise ValueError("Transfer reason cannot be empty")
        return v.strip() if v else None

    @field_validator('transfer_type')
    @classmethod
    def validate_transfer_type(cls, v: str) -> str:
        """Validate transfer type."""
        valid_types = {"transfer", "adoption", "purchase", "gift", "inheritance", "rescue", "return"}
        if v not in valid_types:
            raise ValueError(f"Invalid transfer type: {v}. Must be one of {valid_types}")
        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: datetime | None, info: Any) -> datetime | None:
        """Validate end date."""
        if v is not None and 'start_date' in info.data:
            start_date = info.data['start_date']
            if v <= start_date:
                raise ValueError("End date must be after start date")
        return v

    def is_current_owner(self) -> bool:
        """Check if this is the current owner."""
        return self.end_date is None

    def get_ownership_duration(self) -> int | None:
        """Get ownership duration in days."""
        if self.end_date is None:
            return None
        return (self.end_date - self.start_date).days

    def get_ownership_duration_years(self) -> float | None:
        """Get ownership duration in years."""
        days = self.get_ownership_duration()
        return days / 365.25 if days is not None else None

    def is_adoption(self) -> bool:
        """Check if this is an adoption transfer."""
        return self.transfer_type == "adoption"

    def is_purchase(self) -> bool:
        """Check if this is a purchase transfer."""
        return self.transfer_type == "purchase"

    def is_gift(self) -> bool:
        """Check if this is a gift transfer."""
        return self.transfer_type == "gift"

    def is_rescue(self) -> bool:
        """Check if this is a rescue transfer."""
        return self.transfer_type == "rescue"


class OwnershipHistory(ValueObject):
    """Ownership history value object for tracking pet ownership changes."""

    pet_id: str = Field(..., description="Pet ID")
    ownership_records: list[OwnershipRecord] = Field(
        default_factory=list,
        description="List of ownership records in chronological order"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="History creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    @field_validator('pet_id')
    @classmethod
    def validate_pet_id(cls, v: str) -> str:
        """Validate pet ID."""
        if not v or not v.strip():
            raise ValueError("Pet ID cannot be empty")
        return v.strip()

    @field_validator('ownership_records')
    @classmethod
    def validate_ownership_records(cls, v: list[OwnershipRecord]) -> list[OwnershipRecord]:
        """Validate ownership records."""
        if not v:
            return v
        
        # Check for chronological order
        for i in range(1, len(v)):
            if v[i].start_date < v[i-1].start_date:
                raise ValueError("Ownership records must be in chronological order")
        
        # Check that only the last record can have no end_date
        for i, record in enumerate(v[:-1]):
            if record.end_date is None:
                raise ValueError("Only the last ownership record can have no end_date")
        
        return v

    @classmethod
    def create_empty(cls, pet_id: str) -> "OwnershipHistory":
        """Create an empty ownership history."""
        return cls(pet_id=pet_id, ownership_records=[])

    @classmethod
    def create_with_initial_owner(cls, pet_id: str, owner_id: str, owner_name: str | None = None, 
                                 transfer_type: str = "adoption") -> "OwnershipHistory":
        """Create ownership history with initial owner."""
        initial_record = OwnershipRecord(
            owner_id=owner_id,
            owner_name=owner_name,
            start_date=datetime.utcnow(),
            end_date=None,
            transfer_type=transfer_type
        )
        return cls(pet_id=pet_id, ownership_records=[initial_record])

    def add_ownership_record(self, record: OwnershipRecord) -> "OwnershipHistory":
        """Add a new ownership record."""
        if not self.ownership_records:
            # First record
            new_records = [record]
        else:
            # End the current ownership
            current_records = list(self.ownership_records)
            if current_records:
                last_record = current_records[-1]
                if last_record.end_date is None:
                    # End the current ownership
                    ended_record = last_record.copy_with(end_date=record.start_date)
                    current_records[-1] = ended_record
            
            new_records = current_records + [record]
        
        return self.copy_with(
            ownership_records=new_records,
            updated_at=datetime.utcnow()
        )

    def transfer_ownership(self, new_owner_id: str, new_owner_name: str | None = None,
                          transfer_reason: str | None = None, transfer_type: str = "transfer") -> "OwnershipHistory":
        """Transfer ownership to a new owner."""
        new_record = OwnershipRecord(
            owner_id=new_owner_id,
            owner_name=new_owner_name,
            start_date=datetime.utcnow(),
            end_date=None,
            transfer_reason=transfer_reason,
            transfer_type=transfer_type
        )
        return self.add_ownership_record(new_record)

    def get_current_owner(self) -> OwnershipRecord | None:
        """Get the current owner record."""
        if not self.ownership_records:
            return None
        return self.ownership_records[-1] if self.ownership_records[-1].is_current_owner() else None

    def get_current_owner_id(self) -> str | None:
        """Get the current owner ID."""
        current_owner = self.get_current_owner()
        return current_owner.owner_id if current_owner else None

    def get_previous_owners(self) -> list[OwnershipRecord]:
        """Get all previous owner records."""
        if not self.ownership_records:
            return []
        
        # Return all records except the current one
        return [record for record in self.ownership_records if not record.is_current_owner()]

    def get_ownership_count(self) -> int:
        """Get the total number of owners (including current)."""
        return len(self.ownership_records)

    def get_ownership_duration_for_owner(self, owner_id: str) -> int | None:
        """Get total ownership duration for a specific owner in days."""
        total_days = 0
        found_owner = False
        
        for record in self.ownership_records:
            if record.owner_id == owner_id:
                found_owner = True
                duration = record.get_ownership_duration()
                if duration is not None:
                    total_days += duration
                else:
                    # Current owner, add days since start
                    total_days += (datetime.utcnow() - record.start_date).days
        
        return total_days if found_owner else None

    def get_ownership_summary(self) -> dict[str, Any]:
        """Get ownership summary statistics."""
        if not self.ownership_records:
            return {
                "total_owners": 0,
                "current_owner": None,
                "average_ownership_duration": 0,
                "longest_ownership": 0,
                "shortest_ownership": 0,
                "transfer_types": {}
            }
        
        current_owner = self.get_current_owner()
        previous_owners = self.get_previous_owners()
        
        # Calculate durations for previous owners
        durations = []
        transfer_types = {}
        
        for record in previous_owners:
            duration = record.get_ownership_duration()
            if duration is not None:
                durations.append(duration)
            
            transfer_type = record.transfer_type
            transfer_types[transfer_type] = transfer_types.get(transfer_type, 0) + 1
        
        # Add current owner duration if applicable
        if current_owner:
            current_duration = (datetime.utcnow() - current_owner.start_date).days
            durations.append(current_duration)
        
        return {
            "total_owners": len(self.ownership_records),
            "current_owner": {
                "owner_id": current_owner.owner_id,
                "owner_name": current_owner.owner_name,
                "start_date": current_owner.start_date.isoformat(),
                "duration_days": current_duration if current_owner else 0
            } if current_owner else None,
            "average_ownership_duration": sum(durations) / len(durations) if durations else 0,
            "longest_ownership": max(durations) if durations else 0,
            "shortest_ownership": min(durations) if durations else 0,
            "transfer_types": transfer_types
        }

    def has_been_owned_by(self, owner_id: str) -> bool:
        """Check if pet has been owned by a specific owner."""
        return any(record.owner_id == owner_id for record in self.ownership_records)

    def get_ownership_timeline(self) -> list[dict[str, Any]]:
        """Get ownership timeline as a list of events."""
        timeline = []
        
        for record in self.ownership_records:
            timeline.append({
                "event_type": "ownership_start",
                "owner_id": record.owner_id,
                "owner_name": record.owner_name,
                "date": record.start_date.isoformat(),
                "transfer_type": record.transfer_type,
                "transfer_reason": record.transfer_reason
            })
            
            if record.end_date:
                timeline.append({
                    "event_type": "ownership_end",
                    "owner_id": record.owner_id,
                    "owner_name": record.owner_name,
                    "date": record.end_date.isoformat(),
                    "duration_days": record.get_ownership_duration()
                })
        
        return sorted(timeline, key=lambda x: x["date"])

    def __len__(self) -> int:
        """Return the number of ownership records."""
        return len(self.ownership_records)

    def __str__(self) -> str:
        """String representation of the ownership history."""
        current_owner = self.get_current_owner()
        owner_count = len(self.ownership_records)
        
        if current_owner:
            return f"Pet {self.pet_id} - {owner_count} owners, current: {current_owner.owner_id}"
        else:
            return f"Pet {self.pet_id} - {owner_count} owners, no current owner"
