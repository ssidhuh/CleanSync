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

    The booking entity centralises scheduling and workflow
    behaviour to reduce business logic inside the UI layer.
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

    ACTIVE_STATUSES = {
        "Pending",
        "Confirmed",
        "In Progress",
        "Assigned",
    }

    COMPLETED_STATUSES = {
        "Completed",
        "Cancelled",
    }

    @property
    def is_active(self) -> bool:
        """Keep workflow state checks encapsulated inside the entity."""
        return self.status in self.ACTIVE_STATUSES

    @property
    def is_completed(self) -> bool:
        """Avoid duplicated completion checks across multiple views."""
        return self.status in self.COMPLETED_STATUSES

    @property
    def duration_hours(self) -> float:
        """Provide reusable booking duration calculations."""
        if self.end_time is None:
            return 0.0

        duration = (
            self.end_time - self.booking_date
        ).total_seconds() / 3600

        return round(duration, 2)

    def confirm_booking(self) -> None:
        """Synchronise cleaner availability with booking workflow."""
        self.status = "Confirmed"
        self.cleaner.mark_unavailable()

    def complete_booking(self) -> None:
        """Release cleaner availability after booking completion."""
        self.status = "Completed"
        self.cleaner.mark_available()

    def cancel_booking(self) -> None:
        """Keep cancellation behaviour controlled by the entity."""
        self.status = "Cancelled"
        self.cleaner.mark_available()

    def start_booking(self) -> None:
        """Prevent direct workflow manipulation from external layers."""
        self.status = "In Progress"
        self.cleaner.mark_unavailable()

    def validate_schedule(self) -> bool:
        """Keep scheduling rules independent from the UI layer."""
        if self.end_time is None:
            return False

        return self.end_time > self.booking_date

    def calculate_total_amount(self) -> float:
        """Centralise financial calculations for reuse across the system."""
        calculated_total = (
            self.duration_hours * self.cleaner.hourly_rate
        )

        return round(calculated_total, 2)

    def update_total_amount(self) -> None:
        """Maintain consistency between schedule and pricing data."""
        self.total_amount = self.calculate_total_amount()

    def has_notes(self) -> bool:
        """Improve readability when checking operational notes."""
        return bool(self.notes.strip())

    def reschedule_booking(
        self,
        new_start_time: datetime,
        new_end_time: datetime,
    ) -> None:
        """Keep rescheduling behaviour encapsulated inside the entity."""
        self.booking_date = new_start_time
        self.end_time = new_end_time

        self.__validate_rescheduled_times()
        self.update_total_amount()

    def __validate_rescheduled_times(self) -> None:
        """Restrict internal validation logic from external access."""
        if self.end_time is None:
            raise ValueError("End time is required.")

        if self.end_time <= self.booking_date:
            raise ValueError(
                "End time must be after the booking start time."
            )
