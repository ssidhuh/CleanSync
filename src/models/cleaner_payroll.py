"""Cleaner payroll entity module."""

from dataclasses import dataclass
from datetime import datetime

from src.models.base_entity import BaseEntity


@dataclass
class CleanerPayroll(BaseEntity):
    """
    Represents weekly cleaner earnings calculated from completed bookings.

    Payroll is separated from customer invoices because cleaner earnings are
    an internal business cost, while customer invoices are external billing.
    """

    cleaner_name: str
    week_start: datetime
    week_end: datetime
    completed_bookings: int
    total_hours: float
    hourly_pay_rate: float
    total_earnings: float
    payment_status: str

    @property
    def period_text(self) -> str:
        """Return a readable weekly payment period."""
        return (
            f"{self.week_start.strftime('%d %b %Y')} - "
            f"{self.week_end.strftime('%d %b %Y')}"
        )
