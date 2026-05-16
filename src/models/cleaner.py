"""Cleaner entity module."""

from dataclasses import dataclass

from src.models.base_entity import BaseEntity


@dataclass
class Cleaner(BaseEntity):
    """
    Represents an employee assigned to cleaning bookings.

    The cleaner entity stores profile, availability, rating and
    specialisation details used by the scheduling interface.
    """

    first_name: str
    last_name: str
    email: str
    phone_number: str
    hourly_rate: float
    rating: float
    status: str
    specializations: str
    service_area: str = ""

    @property
    def full_name(self) -> str:
        """Return the cleaner's display name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_available(self) -> bool:
        """Return whether the cleaner can currently be assigned."""
        return self.status.lower() == "available"

    def mark_unavailable(self) -> None:
        """Mark the cleaner as on job after booking assignment."""
        self.status = "On Job"

    def mark_available(self) -> None:
        """Mark the cleaner as available after completion or cancellation."""
        self.status = "Available"

    def validate_profile(self) -> bool:
        """Validate minimum cleaner profile details before saving."""
        return (
            "@" in self.email
            and len(self.phone_number) >= 8
            and self.hourly_rate > 0
            and 1 <= self.rating <= 5
        )