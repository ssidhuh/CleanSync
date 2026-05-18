"""Booking entity module."""

from dataclasses import dataclass
from datetime import datetime

from src.models.base_entity import BaseEntity
from src.models.cleaner import Cleaner
from src.models.customer import Customer
from src.models.service import CleaningService


@dataclass
class Booking(BaseEntity):
    """
    Represents a scheduled cleaning appointment.

    The booking entity coordinates relationships between
    customers, cleaners, and cleaning services.
    """

    customer: Customer
    cleaner: Cleaner
    cleaning_service: CleaningService
    booking_date: datetime
    status: str
    booking_number: str = ""
    end_time: datetime | None = None
    address: str = ""
    total_amount: float = 0.0
    notes: str = ""

    def confirm_booking(self) -> None:
        """Confirm the booking after validation and assignment."""
        self.status = "Confirmed"
        self.cleaner.mark_unavailable()

    def complete_booking(self) -> None:
        """Complete the booking and release cleaner availability."""
        self.status = "Completed"
        self.cleaner.mark_available()

    def cancel_booking(self) -> None:
        """Cancel the booking and release cleaner availability."""
        self.status = "Cancelled"
        self.cleaner.mark_available()
