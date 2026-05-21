"""Cleaner payroll entity module."""

from dataclasses import dataclass
from datetime import datetime

from src.models.base_entity import BaseEntity


@dataclass
class CleanerPayroll(BaseEntity):
    """
    Represents weekly cleaner earnings calculated from completed bookings.

    Payroll is kept as a separate entity because internal cleaner earnings
    should not be mixed with customer invoice data.
    """

    cleaner_name: str
    week_start: datetime
    week_end: datetime
    completed_bookings: int
    total_hours: float
    hourly_pay_rate: float
    total_earnings: float
    payment_status: str

    PAID_STATUS = "Paid"
    PENDING_STATUS = "Pending"

    @property
    def period_text(self) -> str:
        """Provide one reusable weekly payment period format."""
        return (
            f"{self.week_start.strftime('%d %b %Y')} - "
            f"{self.week_end.strftime('%d %b %Y')}"
        )

    @property
    def is_paid(self) -> bool:
        """Keep payroll payment checks inside the payroll entity."""
        return self.payment_status == self.PAID_STATUS

    @property
    def is_pending(self) -> bool:
        """Avoid duplicated pending-state checks inside payroll views."""
        return self.payment_status == self.PENDING_STATUS

    @property
    def average_earning_per_booking(self) -> float:
        """Support payroll reporting without duplicating calculations."""
        if self.completed_bookings <= 0:
            return 0.0

        return round(self.total_earnings / self.completed_bookings, 2)

    def calculate_total_earnings(self) -> float:
        """Keep payroll calculation rules reusable and testable."""
        return round(self.total_hours * self.hourly_pay_rate, 2)

    def refresh_total_earnings(self) -> None:
        """Keep stored earnings aligned with hours and pay rate."""
        self.total_earnings = self.calculate_total_earnings()

    def mark_as_paid(self) -> None:
        """Control payroll workflow state through the entity."""
        self.payment_status = self.PAID_STATUS

    def mark_as_pending(self) -> None:
        """Allow payroll status to be reset without direct field edits."""
        self.payment_status = self.PENDING_STATUS

    def validate_payroll_details(self) -> bool:
        """Keep payroll validation independent from view-specific code."""
        return (
            self.completed_bookings >= 0
            and self.total_hours >= 0
            and self.hourly_pay_rate > 0
            and self.total_earnings >= 0
        )
