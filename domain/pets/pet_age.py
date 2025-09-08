"""Pet age value object with age calculation logic."""

from datetime import date, datetime
from typing import Any

from pydantic import Field, field_validator

from domain.common.value_object_base import ValueObject


class PetAge(ValueObject):
    """Pet age value object with comprehensive age calculation and validation."""

    birth_date: date | None = Field(None, description="Pet's birth date")
    current_date: date = Field(default_factory=date.today, description="Current date for age calculation")

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: date | None) -> date | None:
        """Validate birth date."""
        if v is not None:
            if v > date.today():
                raise ValueError("Birth date cannot be in the future")
            # Check if birth date is not too far in the past (e.g., 50 years)
            if v < date.today().replace(year=date.today().year - 50):
                raise ValueError("Birth date is too far in the past")
        return v

    @field_validator('current_date')
    @classmethod
    def validate_current_date(cls, v: date) -> date:
        """Validate current date."""
        if v < date.today().replace(year=date.today().year - 1):
            raise ValueError("Current date cannot be more than 1 year in the past")
        if v > date.today():
            raise ValueError("Current date cannot be in the future")
        return v

    @classmethod
    def from_birth_date(cls, birth_date: date | datetime | None) -> "PetAge":
        """Create PetAge from birth date."""
        if birth_date is None:
            return cls(birth_date=None)
        
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        
        return cls(birth_date=birth_date)

    @classmethod
    def from_birth_date_string(cls, birth_date_str: str | None) -> "PetAge":
        """Create PetAge from birth date string."""
        if not birth_date_str:
            return cls(birth_date=None)
        
        try:
            birth_date = datetime.fromisoformat(birth_date_str.replace('Z', '+00:00')).date()
            return cls(birth_date=birth_date)
        except ValueError as e:
            raise ValueError(f"Invalid birth date format: {birth_date_str}") from e

    def get_age_in_days(self) -> int | None:
        """Get age in days."""
        if self.birth_date is None:
            return None
        return (self.current_date - self.birth_date).days

    def get_age_in_weeks(self) -> int | None:
        """Get age in weeks."""
        days = self.get_age_in_days()
        return days // 7 if days is not None else None

    def get_age_in_months(self) -> int | None:
        """Get age in months (approximate)."""
        if self.birth_date is None:
            return None
        
        years = self.current_date.year - self.birth_date.year
        months = self.current_date.month - self.birth_date.month
        
        total_months = years * 12 + months
        
        # Adjust if the day hasn't been reached yet this month
        if self.current_date.day < self.birth_date.day:
            total_months -= 1
        
        return max(0, total_months)

    def get_age_in_years(self) -> int | None:
        """Get age in years."""
        if self.birth_date is None:
            return None
        
        years = self.current_date.year - self.birth_date.year
        
        # Adjust if birthday hasn't occurred yet this year
        if (self.current_date.month, self.current_date.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        
        return max(0, years)

    def get_age_in_years_and_months(self) -> tuple[int, int] | None:
        """Get age as years and months tuple."""
        if self.birth_date is None:
            return None
        
        years = self.get_age_in_years()
        if years is None:
            return None
        
        # Calculate months within the current year
        current_birthday = self.birth_date.replace(year=self.current_date.year)
        if current_birthday > self.current_date:
            current_birthday = current_birthday.replace(year=self.current_date.year - 1)
        
        months = (self.current_date.year - current_birthday.year) * 12 + (self.current_date.month - current_birthday.month)
        months = months % 12
        
        return years, months

    def is_puppy(self) -> bool:
        """Check if pet is a puppy (less than 1 year old)."""
        years = self.get_age_in_years()
        return years is not None and years < 1

    def is_adult(self) -> bool:
        """Check if pet is an adult (1 year or older)."""
        years = self.get_age_in_years()
        return years is not None and years >= 1

    def is_senior(self, senior_age: int = 7) -> bool:
        """Check if pet is a senior (default 7 years or older)."""
        years = self.get_age_in_years()
        return years is not None and years >= senior_age

    def get_life_stage(self) -> str | None:
        """Get pet's life stage."""
        if self.birth_date is None:
            return None
        
        years = self.get_age_in_years()
        if years is None:
            return None
        
        if years < 1:
            return "puppy"
        elif years < 3:
            return "young_adult"
        elif years < 7:
            return "adult"
        else:
            return "senior"

    def get_formatted_age(self) -> str | None:
        """Get formatted age string."""
        if self.birth_date is None:
            return "Unknown"
        
        years, months = self.get_age_in_years_and_months()
        if years is None:
            return "Unknown"
        
        if years == 0:
            if months == 0:
                days = self.get_age_in_days()
                if days is not None and days < 7:
                    return f"{days} day{'s' if days != 1 else ''}"
                else:
                    weeks = self.get_age_in_weeks()
                    return f"{weeks} week{'s' if weeks != 1 else ''}"
            else:
                return f"{months} month{'s' if months != 1 else ''}"
        elif months == 0:
            return f"{years} year{'s' if years != 1 else ''}"
        else:
            return f"{years} year{'s' if years != 1 else ''} and {months} month{'s' if months != 1 else ''}"

    def get_next_birthday(self) -> date | None:
        """Get the next birthday date."""
        if self.birth_date is None:
            return None
        
        next_birthday = self.birth_date.replace(year=self.current_date.year)
        if next_birthday <= self.current_date:
            next_birthday = next_birthday.replace(year=self.current_date.year + 1)
        
        return next_birthday

    def days_until_birthday(self) -> int | None:
        """Get days until next birthday."""
        next_birthday = self.get_next_birthday()
        if next_birthday is None:
            return None
        return (next_birthday - self.current_date).days

    def is_birthday_today(self) -> bool:
        """Check if today is the pet's birthday."""
        if self.birth_date is None:
            return False
        return (self.current_date.month, self.current_date.day) == (self.birth_date.month, self.birth_date.day)

    def with_current_date(self, current_date: date) -> "PetAge":
        """Create a new PetAge with updated current date."""
        return self.copy_with(current_date=current_date)

    def __str__(self) -> str:
        """String representation of the age."""
        return self.get_formatted_age() or "Unknown"

    def __bool__(self) -> bool:
        """Boolean representation - True if birth date is known."""
        return self.birth_date is not None
